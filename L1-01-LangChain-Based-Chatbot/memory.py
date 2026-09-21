"""
memory.py — Conversation Memory Management

Provides a simple in-memory chat history store.
Each session gets its own history so multiple users
(or browser tabs) stay independent.
"""

from langchain_core.chat_history import InMemoryChatMessageHistory

# Dictionary that maps session IDs to their chat history
session_store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Return the chat history for a given session.
    If this session is new, create an empty history.
    """
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


def clear_session_history(session_id: str):
    """Remove all messages from a session's history."""
    if session_id in session_store:
        session_store[session_id].clear()
