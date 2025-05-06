import streamlit as st
from ai_modules.agent_chai import ChAIAgent

# Page setup
st.set_page_config(page_title="ChAI - ChRIS Assistant", layout="wide")

st.markdown("""
    <style>
    .chat-title { text-align: center; font-size: 32px; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='chat-title'>🧠 ChAI — ChRIS Medical Assistant</div>", unsafe_allow_html=True)
st.caption("Ask about ChRIS workflows, plugins, or pipelines.")

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

if "agent" not in st.session_state:
    st.session_state.agent = ChAIAgent()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("context"):
            with st.expander("📄 Retrieved Context", expanded=False):
                for doc in msg["context"]:
                    source = doc["metadata"].get("source", "unknown") if isinstance(doc, dict) else getattr(doc, "metadata", {}).get("source", "unknown")
                    content = doc.get("content", str(doc)) if isinstance(doc, dict) else getattr(doc, "content", str(doc))
                    st.markdown(f"**Source:** `{source}`")
                    st.markdown(f"> {content.strip()}")
                    st.markdown("---")

# Handle input
query = st.chat_input("What would you like to ask?")

if query:
    # Show user input
    st.chat_message("user").markdown(query)

    # Append user input to messages and memory
    user_msg = {"role": "user", "content": query}
    st.session_state.messages.append(user_msg)
    st.session_state.memory.append(user_msg)

    # Stream response
    response_text = ""
    context_docs = []

    with st.chat_message("assistant"):
        response_box = st.empty()

        for result in st.session_state.agent.ask(query, st.session_state.memory, stream=True):
            if isinstance(result, dict) and "context" in result:
                context_docs = result["context"]
            elif isinstance(result, str):
                response_text += result
                response_box.markdown(response_text)

    # Final assistant message (without 'context' in memory)
    assistant_msg = {
        "role": "assistant",
        "content": response_text,
        "context": context_docs
    }

    st.session_state.messages.append(assistant_msg)
    st.session_state.memory.append({
        "role": "assistant",
        "content": response_text.strip()
    })

