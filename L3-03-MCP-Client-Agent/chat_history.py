"""
=============================================================
CHAT HISTORY (In-Memory)
=============================================================
Purpose:
    Manages chat conversations in memory using Streamlit session state.
    No files are saved to disk — everything lives in the session.

Why we need it:
    - Supports "New Chat" and "Recent Chats" in the sidebar
    - Keeps conversation history for Gemini context
    - Groups chats by date (Today, Yesterday, Older)

How it connects:
    - app.py calls these functions to manage conversations
    - The sidebar shows recent chats from this module
    - Messages are stored in st.session_state
=============================================================
"""

import uuid
from datetime import datetime


def init_chat_state(session_state):
    """
    Initialize chat-related session state if not already set.
    Call this at the start of every Streamlit page load.
    """
    if "chats" not in session_state:
        session_state.chats = {}           # All chats: {chat_id: chat_data}
    if "current_chat_id" not in session_state:
        session_state.current_chat_id = None  # Currently active chat


def create_chat(session_state):
    """
    Create a new empty chat and make it the active chat.

    Returns:
        str: The new chat's ID
    """
    chat_id = str(uuid.uuid4())[:8]  # Short unique ID
    session_state.chats[chat_id] = {
        "chat_id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": [],                    # List of {"role": ..., "content": ...}
    }
    session_state.current_chat_id = chat_id
    return chat_id


def get_current_chat(session_state):
    """Get the currently active chat data, or None."""
    chat_id = session_state.get("current_chat_id")
    if chat_id and chat_id in session_state.chats:
        return session_state.chats[chat_id]
    return None


def add_message(session_state, role: str, content: str):
    """
    Add a message to the current chat.

    Args:
        role: "user" or "assistant"
        content: The message text
    """
    chat = get_current_chat(session_state)
    if not chat:
        return

    chat["messages"].append({
        "role": role,
        "content": content,
    })

    # Auto-generate title from the first user message
    if role == "user" and chat["title"] == "New Chat":
        chat["title"] = generate_title(content)


def generate_title(message: str) -> str:
    """
    Generate a simple chat title from the first user message.
    No LLM call — just simple Python string manipulation.

    Examples:
        "What is the weather in Pune?" → "Weather in Pune"
        "Calculate 25 * 8 + 10"       → "Calculate 25 * 8 + 10"
        "Tell me about MCP protocol"  → "Tell me about MCP protocol"
    """
    # Clean up the message
    title = message.strip()

    # Remove common question starters
    for prefix in ["what is the ", "what's the ", "can you ", "please ", "tell me "]:
        if title.lower().startswith(prefix):
            title = title[len(prefix):]
            break

    # Remove trailing punctuation
    title = title.rstrip("?.!")

    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]

    # Truncate if too long
    if len(title) > 50:
        title = title[:50] + "..."

    return title or "New Chat"


def get_recent_chats(session_state):
    """
    Get all chats grouped by date for the sidebar.

    Returns:
        dict: {"Today": [...], "Yesterday": [...], "Older": [...]}
    """
    today = datetime.now().date()
    groups = {"Today": [], "Yesterday": [], "Older": []}

    # Sort chats by creation time (newest first)
    sorted_chats = sorted(
        session_state.chats.values(),
        key=lambda c: c["created_at"],
        reverse=True,
    )

    for chat in sorted_chats:
        try:
            chat_date = datetime.fromisoformat(chat["created_at"]).date()
            days_ago = (today - chat_date).days

            if days_ago == 0:
                groups["Today"].append(chat)
            elif days_ago == 1:
                groups["Yesterday"].append(chat)
            else:
                groups["Older"].append(chat)
        except (ValueError, KeyError):
            groups["Older"].append(chat)

    return groups
