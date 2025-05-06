import streamlit as st
import json
from pathlib import Path
from agents.chai import ChAIAgent
from memory.chroma_store import ChromaMemoryStore

# ✅ Toggle between ChromaDB and JSON memory
USE_CHROMA = True
CHAT_HISTORY_FILE = Path(".chat_history.json")

def load_json_history():
    if CHAT_HISTORY_FILE.exists():
        return json.loads(CHAT_HISTORY_FILE.read_text())
    return []

def save_json_history(history):
    CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2))

# 🧠 Load chat history into session state
if "chat_history" not in st.session_state:
    if USE_CHROMA:
        st.session_state.chat_history = ChromaMemoryStore("chat_memory").get_messages()
    else:
        st.session_state.chat_history = load_json_history()

# ✅ Initialize agent + memory backend
agent = ChAIAgent()
memory_store = ChromaMemoryStore("chat_memory") if USE_CHROMA else None

# 🎨 UI Setup
st.set_page_config(page_title="ChAI - ChRIS Assistant", layout="wide")
st.title("🧠 ChAI - Your ChRIS Assistant")

# 🗃️ Render message history with RAG context (if any)
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("context"):
            with st.expander("📚 Show RAG Documents", expanded=False):  # Default: collapsed
                for i, doc in enumerate(msg["context"]):
                    preview = doc[:1000] if isinstance(doc, str) else str(doc)
                    st.markdown(f"**Doc {i+1}:**\n```text\n{preview}\n```")

# 💬 Chat input and streaming response
if prompt := st.chat_input("Ask your question about ChRIS..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    if USE_CHROMA:
        memory_store.append_message("user", prompt)

    with st.chat_message("assistant"):
        response_container = st.empty()
        response = ""
        context_block = None

        for chunk in agent.ask(prompt, stream=True):  # ✅ Removed `memory=...`
            if isinstance(chunk, dict) and "context" in chunk:
                context_block = chunk["context"]
                with st.expander("📚 Show RAG Documents", expanded=False):
                    for i, doc in enumerate(context_block):
                        preview = doc[:1000] if isinstance(doc, str) else str(doc)
                        st.markdown(f"**Doc {i+1}:**\n```text\n{preview}\n```")
            else:
                response += chunk
                response_container.markdown(response)

    # 🧠 Store assistant message + context
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "context": context_block
    })

    # 💾 Persist memory
    if USE_CHROMA:
        memory_store.append_message("assistant", response)
    else:
        save_json_history(st.session_state.chat_history)
