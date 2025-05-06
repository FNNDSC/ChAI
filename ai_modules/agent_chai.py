import os
import json
import uuid
import logging
from pathlib import Path

from llama_stack_client import LlamaStackClient, Agent, RAGDocument
from llama_stack_client.types import UserMessage
from llama_stack_client.lib.agents.event_logger import EventLogger


class ChAIAgent:
    def __init__(self, base_url="http://localhost:8321", docs_dir="docs"):
        self.client = LlamaStackClient(base_url=base_url)
        self.model = "llama3.2:3b"
        self.vector_db = "demo"
        self.embedding_model = "all-MiniLM-L6-v2"
        self.embedding_dim = 384
        self.docs_dir = Path(docs_dir)

        self._setup_logging()
        self._ensure_vector_db()
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
        else:
            logging.info(f"ℹ️ Vector DB '{self.vector_db}' already exists.")

    def _ingest_documents(self):
        folder = self.docs_dir / self.vector_db
        if not folder.exists():
            logging.warning(f"⚠️ Docs folder '{folder}' not found. Skipping ingestion.")
            return

        documents = []
        for file in folder.rglob("*"):
            if file.suffix.lower() in {".jsonl", ".md", ".txt", ".adoc"}:
                try:
                    if file.suffix == ".jsonl":
                        with open(file, "r", encoding="utf-8") as f:
                            for line in f:
                                obj = json.loads(line)
                                documents.append(RAGDocument(
                                    document_id=str(uuid.uuid4()),
                                    content=obj["text"],
                                    metadata=obj.get("metadata", {"filename": file.name}),
                                    mime_type="text/plain"
                                ))
                    else:
                        content = file.read_text(encoding="utf-8")
                        documents.append(RAGDocument(
                            document_id=str(uuid.uuid4()),
                            content=content,
                            metadata={"filename": file.name},
                            mime_type="text/plain"
                        ))
                    logging.info(f"📄 Prepared: {file}")
                except Exception as e:
                    logging.warning(f"⚠️ Skipped {file.name}: {e}")

        if documents:
            self.client.tool_runtime.rag_tool.insert(
                documents=documents,
                vector_db_id=self.vector_db,
                chunk_size_in_tokens=512,
            )
            logging.info(f"📦 Ingested {len(documents)} into '{self.vector_db}'")

    def ask(self, question: str, memory: list = [], stream: bool = False):
        logging.info(f"🤖 Asking: {question}")

        # Step 1: Fetch context via RAG
        rag_agent = Agent(
            self.client,
            model=self.model,
            instructions="Use the RAG tool to retrieve helpful ChRIS-related context.",
            tools=[{
                "name": "builtin::rag/knowledge_search",
                "args": {
                    "vector_db_ids": [self.vector_db],
                    "top_k": 5
                }
            }],
        )
        rag_session_id = rag_agent.create_session("rag-context")
        rag_turn = rag_agent.create_turn(
            messages=[UserMessage(role="user", content=question)],
            session_id=rag_session_id,
            stream=False,
        )

        # Extract context docs from tool response
        tool_step = next((s for s in rag_turn.steps if s.step_type == "tool_execution"), None)
        tool_context = tool_step.tool_responses[0].content if tool_step else ""
        context_docs = tool_context if isinstance(tool_context, list) else []

        yield {"context": context_docs}  # For UI context rendering

        # Step 2: Build prompt using context
        prompt = (
            "You are an expert assistant for the ChRIS platform.\n"
            "Use only the provided documentation context to answer the question clearly and accurately.\n\n"
            f"User Question:\n{question}\n\n"
            f"Context:\n{tool_context}\n\n"
            "Answer:"
        )

        # Step 3: Create answer using context-aware agent
        answer_agent = Agent(
            self.client,
            model=self.model,
            instructions="Respond using retrieved context only. No assumptions.",
        )
        session_id = answer_agent.create_session("chris-qa")

        # Convert memory to Message objects
        message_history = []
        for m in memory:
            if m["role"] == "user":
                message_history.append(UserMessage(role="user", content=m["content"]))
            elif m["role"] == "assistant":
                message_history.append(UserMessage(role="user", content=m["content"]))  # Treated as 'user' content

        message_history.append(UserMessage(role="user", content=prompt))

        turn = answer_agent.create_turn(
            messages=message_history,
            session_id=session_id,
            stream=stream,
        )

        if stream:
            for step in EventLogger().log(turn):
                if hasattr(step, "content"):
                    yield step.content
        else:
            yield turn.output_message.content

