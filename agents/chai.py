import os
import json
import logging
from pathlib import Path
from llama_stack_client import LlamaStackClient, Agent, RAGDocument
from llama_stack_client.types import UserMessage
from llama_stack_client.lib.agents.event_logger import EventLogger
from memory.chroma_store import ChromaMemoryStore

# Optional PDF support
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

USE_CHROMA = True
CHAT_HISTORY_FILE = Path(".chat_history.json")


def load_json_history():
    if CHAT_HISTORY_FILE.exists():
        return json.loads(CHAT_HISTORY_FILE.read_text())
    return []


class ChAIAgent:
    def __init__(self, base_url="http://localhost:8321", docs_dir="docs"):
        self.client = LlamaStackClient(base_url=base_url)
        self.model = "llama3.2:3b"
        self.vector_db = "demo"
        self.embedding_model = "all-MiniLM-L6-v2"
        self.embedding_dim = 384
        self.docs_dir = Path(docs_dir)

        self._setup_logging()
        created = self._ensure_vector_db()
        if created or self._vector_db_empty():
            self._ingest_documents()

    def _setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "chai_agent.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger().addHandler(console)

    def _ensure_vector_db(self):
        existing = [db.provider_resource_id for db in self.client.vector_dbs.list()]
        if self.vector_db not in existing:
            self.client.vector_dbs.register(
                vector_db_id=self.vector_db,
                embedding_model=self.embedding_model,
                embedding_dimension=self.embedding_dim,
                provider_id="faiss",
            )
            logging.info(f"✅ Registered vector DB: {self.vector_db}")
            return True
        logging.info(f"ℹ️ Vector DB '{self.vector_db}' already exists.")
        return False

    def _vector_db_empty(self):
        try:
            agent = Agent(
                self.client,
                model=self.model,
                instructions="Check for docs",
                tools=[{
                    "name": "builtin::rag/knowledge_search",
                    "args": {"vector_db_ids": [self.vector_db], "top_k": 1}
                }],
            )
            session = agent.create_session("probe")
            turn = agent.create_turn(
                messages=[UserMessage(role="user", content="...")],
                session_id=session,
                stream=False,
            )
            tool_step = next((s for s in turn.steps if s.step_type == "tool_execution"), None)
            docs = tool_step.tool_responses[0].content if tool_step else []
            return len(docs) == 0
        except Exception as e:
            logging.warning(f"⚠️ Probe failed: {e}")
            return False

    def _get_existing_doc_ids(self):
        try:
            agent = Agent(
                self.client,
                model=self.model,
                instructions="Fetch existing doc IDs",
                tools=[{
                    "name": "builtin::rag/knowledge_search",
                    "args": {"vector_db_ids": [self.vector_db], "top_k": 1000}
                }],
            )
            session = agent.create_session("doc-fetch")
            turn = agent.create_turn(
                messages=[UserMessage(role="user", content="list")],
                session_id=session,
                stream=False,
            )
            tool_step = next((s for s in turn.steps if s.step_type == "tool_execution"), None)
            docs = tool_step.tool_responses[0].content if tool_step else []
            return {doc.get("document_id") for doc in docs if isinstance(doc, dict)}
        except Exception as e:
            logging.warning(f"⚠️ Failed to fetch docs: {e}")
            return set()

    def _ingest_documents(self):
        folder = self.docs_dir / self.vector_db
        if not folder.exists():
            logging.warning(f"⚠️ Folder not found: {folder}")
            return

        allowed_exts = {".jsonl", ".md", ".txt", ".adoc"}
        if PdfReader:
            allowed_exts.add(".pdf")
        else:
            logging.warning("⚠️ PDF support missing (PyPDF2)")

        existing_ids = self._get_existing_doc_ids()
        documents = []

        for file in folder.rglob("*"):
            if file.suffix.lower() not in allowed_exts:
                continue
            try:
                if file.suffix == ".jsonl":
                    with open(file, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            doc_id = f"{file.name}#{i}"
                            if doc_id in existing_ids:
                                continue
                            obj = json.loads(line)
                            documents.append(RAGDocument(
                                document_id=doc_id,
                                content=obj["text"],
                                metadata=obj.get("metadata", {"filename": file.name}),
                                mime_type="text/plain"
                            ))

                elif file.suffix == ".pdf" and PdfReader:
                    if file.name in existing_ids:
                        continue
                    reader = PdfReader(file)
                    text = "\n".join([page.extract_text() or "" for page in reader.pages])
                    documents.append(RAGDocument(
                        document_id=file.name,
                        content=text,
                        metadata={"filename": file.name},
                        mime_type="application/pdf"
                    ))

                else:
                    if file.name in existing_ids:
                        continue
                    content = file.read_text(encoding="utf-8")
                    documents.append(RAGDocument(
                        document_id=file.name,
                        content=content,
                        metadata={"filename": file.name},
                        mime_type="text/plain"
                    ))

                logging.info(f"📄 Prepared: {file.name}")

            except Exception as e:
                logging.warning(f"⚠️ Skipped {file.name}: {e}")

        if documents:
            inserted = self.client.tool_runtime.rag_tool.insert(
                documents=documents,
                vector_db_id=self.vector_db,
                chunk_size_in_tokens=512,
            )
            logging.info(f"📦 Inserted {len(documents)} documents into '{self.vector_db}'")
        else:
            logging.info("ℹ️ No new documents to ingest.")

    def ask(self, question: str, stream: bool = False):
        logging.info(f"🤖 Asking: {question}")
        memory = (
            ChromaMemoryStore("chat_memory").get_messages()
            if USE_CHROMA else load_json_history()
        )

        # 🔍 First get context with RAG
        rag_agent = Agent(
            self.client,
            model=self.model,
            instructions="Use the RAG tool to retrieve helpful ChRIS-related context.",
            tools=[{
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [self.vector_db], "top_k": 5}
            }],
        )
        rag_session = rag_agent.create_session("rag-context")
        rag_turn = rag_agent.create_turn(
            messages=[UserMessage(role="user", content=question)],
            session_id=rag_session,
            stream=False,
        )

        steps = list(rag_turn.steps) if hasattr(rag_turn, "steps") else []
        tool_step = next((s for s in steps if s.step_type == "tool_execution"), None)
        tool_context = tool_step.tool_responses[0].content if tool_step else ""
        context_docs = tool_context if isinstance(tool_context, list) else []

        logging.info(f"📚 Retrieved {len(context_docs)} docs")
        yield {"context": context_docs}

        # 🧠 Prepare prompt
        prompt = (
            "You are an expert assistant for the ChRIS platform.\n"
            "Use only the provided documentation context to answer the question clearly and accurately.\n\n"
            f"User Question:\n{question}\n\n"
            f"Context:\n{tool_context}\n\n"
            "Answer:"
        )

        # 💬 Final answer agent
        answer_agent = Agent(
            self.client,
            model=self.model,
            instructions="Respond using retrieved context only. No assumptions.",
        )
        session = answer_agent.create_session("chris-qa")
        message_history = [UserMessage(role="user", content=m["content"]) for m in memory]
        message_history.append(UserMessage(role="user", content=prompt))

        turn = answer_agent.create_turn(
            messages=message_history,
            session_id=session,
            stream=stream,
        )

        if stream:
            for step in EventLogger().log(turn):
                if hasattr(step, "content"):
                    yield step.content
        else:
            yield turn.output_message.content
