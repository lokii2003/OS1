"""
=============================================================
STREAMLIT MAIN APP — Chat Interface
=============================================================
Purpose:
    This is the main Streamlit page. It provides a ChatGPT-like
    chat interface where users can talk to the AI agent.

Why we need it:
    The user interacts with the project through this interface.
    It shows messages, tool execution details, and server status.

How it connects:
    - User types a message → calls agent.process_message()
    - Agent returns response + tool execution info
    - This page displays everything nicely

Run:
    streamlit run app.py
=============================================================
"""

import streamlit as st
import agent
from chat_history import (
    init_chat_state, create_chat, get_current_chat,
    add_message, get_recent_chats,
)
from logger import log

# -----------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------
st.set_page_config(
    page_title="MCP Agent",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for a clean, modern look
st.markdown("""
<style>
    /* Tighter layout */
    .block-container { padding-top: 2rem; }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    section[data-testid="stSidebar"] .stMarkdown { color: #e0e0e0; }

    /* Chat button styling */
    .chat-btn {
        background: none;
        border: none;
        color: #b0b0b0;
        text-align: left;
        padding: 0.3rem 0.5rem;
        width: 100%;
        cursor: pointer;
        border-radius: 0.3rem;
        font-size: 0.85rem;
    }
    .chat-btn:hover { background-color: #2a2a4a; color: white; }

    /* Server status badges */
    .server-status {
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# INITIALIZE SESSION STATE
# -----------------------------------------------
init_chat_state(st.session_state)

# Initialize tool execution storage for the current response
if "tool_executions" not in st.session_state:
    st.session_state.tool_executions = {}  # {message_index: [executions]}

# -----------------------------------------------
# SIDEBAR
# -----------------------------------------------
with st.sidebar:
    st.title("🤖 MCP Agent")
    st.caption("Custom AI Agent + MCP + Gemini")

    st.divider()

    # --- New Chat Button ---
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_chat(st.session_state)
        st.rerun()

    st.divider()

    # --- Recent Chats ---
    st.markdown("**💬 Recent Chats**")
    chat_groups = get_recent_chats(st.session_state)

    for group_name, chats in chat_groups.items():
        if chats:  # Only show groups that have chats
            st.caption(group_name)
            for chat in chats:
                # Highlight the active chat
                is_active = chat["chat_id"] == st.session_state.current_chat_id
                label = f"{'▶ ' if is_active else ''}{chat['title']}"
                if st.button(
                    label,
                    key=f"chat_{chat['chat_id']}",
                    use_container_width=True,
                    disabled=is_active,
                ):
                    st.session_state.current_chat_id = chat["chat_id"]
                    st.rerun()

    st.divider()

    # --- MCP Server Status ---
    st.markdown("**🔌 MCP Servers**")

    # Check server status (cached per session to avoid repeated calls)
    if "server_status" not in st.session_state:
        st.session_state.server_status = {}

    if st.button("🔄 Refresh Status", use_container_width=True):
        with st.spinner("Checking servers..."):
            st.session_state.server_status = agent.get_server_status()
        st.rerun()

    # Display server status
    for server_id, status in st.session_state.server_status.items():
        if status.get("status") == "connected":
            st.success(f"🟢 {status['name']} — {status['tool_count']} tools", icon="✅")
        else:
            st.error(f"🔴 {status['name']} — Disconnected", icon="❌")

    if not st.session_state.server_status:
        st.info("Click 'Refresh Status' to check servers")


# -----------------------------------------------
# MAIN CHAT AREA
# -----------------------------------------------
st.header("🤖 MCP Agent Chat")
st.caption("Powered by Gemini 2.5 Flash + MCP Protocol")

# Get or create current chat
current_chat = get_current_chat(st.session_state)

if not current_chat:
    # No chat exists yet — show welcome message
    st.markdown("""
    ### 👋 Welcome!

    I'm an AI agent powered by **Gemini 2.5 Flash** with **MCP tool integration**.

    I can help you with:
    - 🌤️ **Weather** — "What is the weather in Pune?"
    - 🕐 **Time** — "What time is it in India?"
    - 🧮 **Calculator** — "Calculate 25 * 8 + 10"
    - 💡 **General questions** — "Explain what MCP is"

    **Click "New Chat" to start!**
    """)
else:
    # Display existing messages
    for i, msg in enumerate(current_chat["messages"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Show tool execution details if available for this message
            if i in st.session_state.tool_executions:
                for exec_info in st.session_state.tool_executions[i]:
                    with st.expander("🔧 Tool Execution Details", expanded=False):
                        st.markdown(f"**MCP Server:** {exec_info['server_name']}")
                        st.markdown(f"**Tool:** `{exec_info['tool_name']}`")
                        st.markdown("**Arguments:**")
                        st.json(exec_info["arguments"])
                        status = "✅ Success" if exec_info["success"] else "❌ Failed"
                        st.markdown(f"**Status:** {status}")
                        if exec_info.get("result"):
                            st.markdown("**Result:**")
                            st.code(exec_info["result"])

    # --- Chat Input ---
    user_input = st.chat_input("Ask anything...")

    if user_input:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Save user message
        add_message(st.session_state, "user", user_input)

        # Process through the agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                log(f"Processing: {user_input}")

                # Call the AI agent
                result = agent.process_message(
                    user_message=user_input,
                    chat_messages=current_chat["messages"][:-1],  # Exclude the just-added message
                )

                # Display the response
                st.markdown(result["response"])

                # Show tool execution details
                if result["tool_executions"]:
                    for exec_info in result["tool_executions"]:
                        with st.expander("🔧 Tool Execution Details", expanded=True):
                            st.markdown(f"**MCP Server:** {exec_info['server_name']}")
                            st.markdown(f"**Tool:** `{exec_info['tool_name']}`")
                            st.markdown("**Arguments:**")
                            st.json(exec_info["arguments"])
                            status = "✅ Success" if exec_info["success"] else "❌ Failed"
                            st.markdown(f"**Status:** {status}")
                            if exec_info.get("result"):
                                st.markdown("**Result:**")
                                st.code(exec_info["result"])

        # Save assistant message
        add_message(st.session_state, "assistant", result["response"])

        # Store tool executions for redisplay on rerun
        msg_index = len(current_chat["messages"]) - 1
        if result["tool_executions"]:
            st.session_state.tool_executions[msg_index] = result["tool_executions"]

        # Update server status from the latest discovery
        st.session_state.server_status = agent.get_server_status()
