"""
app.py — Streamlit Frontend

Simple chat interface that connects to the LangChain chatbot.
"""

import streamlit as st
from config import validate_config
from chatbot import get_response
from memory import clear_session_history

# ── Page Configuration ──────────────────────────────────
st.set_page_config(page_title="LangChain AI Chatbot", page_icon="🤖")

# ── Validate API Key on Startup ─────────────────────────
try:
    validate_config()
except ValueError as e:
    st.error(str(e))
    st.stop()

# ── Session State Initialization ────────────────────────
# Streamlit reruns the entire script on every interaction,
# so we store chat messages in session_state to persist them.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "default-session"

# ── Page Header ─────────────────────────────────────────
st.title("🤖 LangChain AI Chatbot")
st.caption("Conversational AI powered by LangChain & Google Gemini")

# ── Sidebar — Clear Chat ────────────────────────────────
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_session_history(st.session_state.session_id)
        st.rerun()

# ── Display Chat History ────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat Input ──────────────────────────────────────────
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Get AI response with a loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = get_response(
                    user_input,
                    st.session_state.session_id,
                )
                st.write(response)
            except Exception as e:
                response = "Sorry, something went wrong. Please try again."
                # Show the actual error
                st.error(f"Error: {e}")
                st.exception(e)

    # Save assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
