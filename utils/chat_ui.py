import streamlit as st

def render_message(msg, role="user"):
    with st.chat_message(role):
        st.markdown(msg)

def scroll_to_bottom():
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
