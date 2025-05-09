import streamlit as st
import json
from pathlib import Path
from agents.chai import ChAIAgent
from memory.chroma_store import ChromaMemoryStore

# ✅ Config
USE_CHROMA = True
CHAT_HISTORY_FILE = Path(".chat_history.json")

def load_json_history():
    if CHAT_HISTORY_FILE.exists():
        return json.loads(CHAT_HISTORY_FILE.read_text())
    return []

def save_json_history(history):
    CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2))

# ── Memory load ────────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    if USE_CHROMA:
        st.session_state.chat_history = ChromaMemoryStore("chat_memory").get_messages()
    else:
        st.session_state.chat_history = load_json_history()

# ── Agent caching ──────────────────────────────────────────────────────────────
# Create the agent (and memory_store) only once, then reuse on every rerun:
if "agent" not in st.session_state:
    st.session_state.agent = ChAIAgent()
    st.session_state.memory_store = (
        ChromaMemoryStore("chat_memory") if USE_CHROMA else None
    )

agent = st.session_state.agent
memory_store = st.session_state.memory_store

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChAI - ChRIS Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styling ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body, .stApp {
        background-color: #111 !important;
        color: #f0f0f0;
    }
    .block-container {
        padding: 1.5rem 2.5rem;
    }
    .stChatMessage {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stChatMessage.user {
        border-left: 4px solid #ff6b81;
    }
    .stChatMessage.assistant {
        border-left: 4px solid #feca57;
    }
    .stExpander {
        background-color: #222 !important;
        color: #eee !important;
    }
    .stChatInputContainer {
        background-color: #181818 !important;
        border: 1px solid #444;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .stTextInput, .stTextArea {
        background-color: #222 !important;
        color: white !important;
    }
    .sidebar .sidebar-content {
        background-color: #0c0c15 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://chrisproject.org/img/logo/ChRISlogo-color.svg", width=60)
    st.markdown("<h2 style='color:#fff;'>ChAI</h2>", unsafe_allow_html=True)
    st.markdown("""
        <p>An open-source assistant for ChRIS (Computational Health Research Integration System).</p>
        <hr style='border-color: #333;'>
        <h4 style='color:#bbb;'>Core Concepts</h4>
        <ul>
        <li><b>Analytics:</b> Visualize & analyze imaging data.</li>
        <li><b>Plugin Container:</b> Run containerized pipelines.</li>
        <li><b>Platform:</b> Open ecosystem for health research.</li>
        </ul>
        <hr style='border-color: #333;'>
        <h4 style='color:#bbb;'>Resources</h4>
        <ul>
        <li><a href='https://chrisproject.org/documentation' target='_blank'>Docs</a></li>
        <li><a href='https://github.com/FNNDSC' target='_blank'>GitHub</a></li>
        </ul>
    """, unsafe_allow_html=True)

# ── Title & History ────────────────────────────────────────────────────────────
st.title("🧠 ChAI")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("context"):
            with st.expander("📚 Show RAG Documents", expanded=False):
                for i, doc in enumerate(msg["context"]):
                    preview = doc[:1000] if isinstance(doc, str) else str(doc)[:1000]
                    st.markdown(f"**Doc {i+1}:**\n```text\n{preview}\n```")

# ── Chat Input & Response ─────────────────────────────────────────────────────
if prompt := st.chat_input("Ask your question about ChRIS..."):
    # Echo user
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save to history & memory
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    if USE_CHROMA:
        memory_store.append_message("user", prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        result = agent.ask(prompt)  # {"content": ..., "context": [...]}

        # 1) Render final answer
        st.markdown(result["content"])

        # 2) Render context if any
        if result["context"]:
            with st.expander("📚 Show RAG Documents", expanded=False):
                for i, chunk in enumerate(result["context"]):
                    preview = chunk[:1000]
                    st.markdown(f"**Doc {i+1}:**\n```text\n{preview}\n```")

    # Append assistant to history & memory
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["content"],
        "context": result["context"]
    })
    if USE_CHROMA:
        memory_store.append_message("assistant", result["content"])
    else:
        save_json_history(st.session_state.chat_history)
