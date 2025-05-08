import os
import json
import yaml
import logging
from pathlib import Path
from typing import List, Any, Dict

from llama_stack_client import LlamaStackClient, Agent, RAGDocument
from llama_stack_client.types import UserMessage
from llama_stack_client.lib.agents.event_logger import EventLogger
from memory.chroma_store import ChromaMemoryStore

from rich.pretty import pprint
from termcolor import cprint

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


# ─── DEFAULT LOGGING (INFO) ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.INFO)

logger = logging.getLogger("ChAIAgent")


USE_CHROMA = True
CHAT_HISTORY_FILE = Path(".chat_history.json")


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_json_history() -> List[dict]:
    if CHAT_HISTORY_FILE.exists():
        data = json.loads(CHAT_HISTORY_FILE.read_text())
        logger.debug("Loaded %d messages from disk history", len(data))
        return data
    logger.debug("No disk history found at %s", CHAT_HISTORY_FILE)
    return []


def save_json_history(history: List[dict]):
    CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2))
    logger.debug("Saved %d messages to disk history", len(history))


def step_printer(steps):
    """
    Print formatted steps when stream=False
    """
    for i, step in enumerate(steps):
        tname = type(step).__name__
        print(f"\n{'-'*10} 📍 Step {i+1}: {tname} {'-'*10}")
        if tname == "ToolExecutionStep":
            print("🔧 Executing tool...")
            try:
                pprint(json.loads(step.tool_responses[0].content))
            except Exception:
                pprint(step.tool_responses[0].content)
        else:
            resp = step.api_model_response
            if resp.content:
                print("🤖 Model Response:")
                cprint(resp.content + "\n", "yellow")
            elif resp.tool_calls:
                call = resp.tool_calls[0]
                print("🛠️ Tool call Generated:")
                cprint(
                    f"Tool call: {call.tool_name}, Arguments: "
                    f"{json.loads(call.arguments_json)}",
                    "yellow"
                )
    print(f"{'='*10} Query processing completed {'='*10}\n")


class ChAIAgent:
    def __init__(self, config_path: str = "config.yaml", thread_id: str = "chat_memory"):
        # Load config & optionally enable DEBUG
        cfg = load_config(config_path)
        lvl = cfg.get("logging", {}).get("level", "").upper()
        debug_flag = cfg.get("llama_stack", {}).get("debug", False)
        if lvl == "DEBUG" or debug_flag:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.getLogger("httpx").setLevel(logging.DEBUG)
            logging.getLogger("chromadb").setLevel(logging.DEBUG)
            logger.debug("DEBUG logging enabled via config")
        else:
            logger.debug("Running with INFO logging")

        logger.info("ChAIAgent Initialized")

        self.config = cfg
        self.thread_id = thread_id

        # Pull MCP URLs from config.yaml
        mcp_cfg = cfg["mcp"]            # KeyError if missing
        self.mcp_url = mcp_cfg["chris_url"].rstrip("/")  # KeyError if missing
        self.sse_url = f"{self.mcp_url}/sse"
        logger.debug("Using MCP server URL: %s", self.mcp_url)

        # LlamaStack client & model
        ls_cfg = cfg["llama_stack"]
        self.client = LlamaStackClient(base_url=ls_cfg["base_url"])
        self.model = ls_cfg["model"]
        logger.debug("LlamaStackClient @ %s, model=%s", ls_cfg["base_url"], self.model)

        # Vector DB settings
        v = cfg["vector_db"]
        self.vector_db = v["id"]
        self.embedding_model = v["embedding_model"]
        self.embedding_dim = v["embedding_dimension"]
        self.chunk_size = v["chunk_size"]
        logger.debug(
            "VectorDB=%s embed_model=%s dim=%d chunk_size=%d",
            self.vector_db, self.embedding_model, self.embedding_dim, self.chunk_size
        )

        # Ingestion settings
        ing = cfg["ingestion"]
        self.docs_dir = Path(ing["local_docs_dir"])
        self.urls = ing.get("remote_urls", [])
        logger.debug("Ingest: docs_dir=%s, remote_urls=%s", self.docs_dir, self.urls)

        # Register toolgroups & ingest docs
        self._register_toolgroups()
        if self._ensure_vector_db():
            self._ingest_documents()

        # Build agent + session
        self.agent = self._create_agent()
        self.session_id = self.agent.create_session("chris_session")
        logger.debug("Session created: %s", self.session_id)

    def _register_toolgroups(self):
        existing = {t.toolgroup_id for t in self.client.tools.list()}
        logger.debug("Existing toolgroups: %s", existing)

        if "builtin::rag" not in existing:
            self.client.toolgroups.register("builtin::rag", provider_id="milvus")
            logger.info("Registered toolgroup: builtin::rag")
        else:
            logger.info("Toolgroup builtin::rag already present")

        if "mcp::chris" not in existing:
            try:
                # point both uri and sse_uri at the SSE endpoint
                self.client.toolgroups.register(
                    toolgroup_id="mcp::chris",
                    provider_id="model-context-protocol",
                    mcp_endpoint={"uri": self.sse_url, "sse_uri": self.sse_url}
                )
                logger.info("Registered toolgroup: mcp::chris")
            except Exception as e:
                logger.warning("Failed registering mcp::chris: %s", e)
        else:
            logger.info("Toolgroup mcp::chris already present")

        # List & log the individual tools by identifier
        try:
            tools = self.client.tools.list(toolgroup_id="mcp::chris")
            tool_ids = [t.identifier for t in tools]
            logger.info("Tools available in mcp::chris: %s", tool_ids)
        except Exception as e:
            logger.warning("Could not fetch tools for mcp::chris: %s", e)

    def _ensure_vector_db(self) -> bool:
        existing = {db.provider_resource_id for db in self.client.vector_dbs.list()}
        if self.vector_db not in existing:
            vcfg = self.config["vector_db"]
            self.client.vector_dbs.register(
                vector_db_id=self.vector_db,
                embedding_model=self.embedding_model,
                embedding_dimension=self.embedding_dim,
                provider_id=vcfg.get("provider_id", "faiss"),
            )
            logger.info("Registered vector DB: %s", self.vector_db)
            return True
        logger.debug("Vector DB %s already exists", self.vector_db)
        return False

    def _ingest_documents(self):
        logger.info("Ingesting docs into VectorDB `%s`", self.vector_db)
        docs: List[RAGDocument] = []

        # Remote URLs
        for i, (url, mime) in enumerate(self.urls):
            docs.append(RAGDocument(f"url-{i}", url, mime, {}))

        # Local files
        for f in self.docs_dir.rglob("*"):
            try:
                if f.suffix == ".pdf" and PdfReader:
                    text = "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
                    docs.append(RAGDocument(f.name, text, "application/pdf", {"source": str(f)}))
                elif f.suffix in {".md", ".txt", ".adoc"}:
                    text = f.read_text(encoding="utf-8")
                    docs.append(RAGDocument(f.name, text, "text/plain", {"source": str(f)}))
            except Exception as e:
                logger.warning("Failed reading %s: %s", f, e)

        if docs:
            self.client.tool_runtime.rag_tool.insert(
                documents=docs,
                vector_db_id=self.vector_db,
                chunk_size_in_tokens=self.chunk_size
            )
            logger.info("Inserted %d documents", len(docs))
        else:
            logger.debug("No docs to ingest in %s", self.docs_dir)

    def _create_agent(self) -> Agent:
        logger.info("Creating RAG+MCP agent")
        return Agent(
            client=self.client,
            model=self.model,
            instructions=self.config["llama_stack"].get(
                "instructions",
                "You are a helpful ChRIS assistant."
            ),
            tools=[
                {"name": "builtin::rag/knowledge_search", "args": {"vector_db_ids": [self.vector_db]}},
                "mcp::chris"
            ],
            tool_config={"tool_choice": "auto"},
            sampling_params={"max_tokens": 4096}
        )

    def ask(self, prompt: str, stream: bool = False) -> dict:
        logger.debug("ask() ➞ prompt=%r, stream=%s", prompt, stream)

        # 1) Load history
        raw = (
            ChromaMemoryStore(self.thread_id).get_messages()
            if USE_CHROMA else load_json_history()
        )
        logger.debug("Raw history: %s", raw)

        # 2) Filter only user messages
        history = [UserMessage(role="user", content=m["content"]) for m in raw if m.get("role") == "user"]
        history.append(UserMessage(role="user", content=prompt))
        logger.debug("History → %s", history)

        # 3) Call the agent
        resp = self.agent.create_turn(
            messages=history,
            session_id=self.session_id,
            stream=stream
        )

        # 4) Stream vs non-stream
        if stream:
            for entry in EventLogger().log(resp):
                entry.print()
            return {}

        # Non-stream: print steps & collect context
        step_printer(resp.steps)
        context = [
            item.text
            for step in resp.steps
            if getattr(step, "tool", None) == "builtin::rag/knowledge_search"
            for item in step.output
        ]
        content = resp.output_message.content
        logger.debug("Assistant → %r", content)
        return {"content": content, "context": context}
