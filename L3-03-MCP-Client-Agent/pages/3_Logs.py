"""
=============================================================
LOGS PAGE
=============================================================
Purpose:
    Displays the execution logs from the current session.
    Shows the step-by-step agent workflow for debugging.
=============================================================
"""

import streamlit as st
from logger import get_logs, clear_logs

st.set_page_config(page_title="Logs", page_icon="📋", layout="wide")

st.header("📋 Execution Logs")
st.caption("Step-by-step agent workflow logs from the current session")

# Controls
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🗑️ Clear Logs"):
        clear_logs()
        st.rerun()

with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

st.divider()

# Get and display logs
logs = get_logs()

if not logs:
    st.info("No logs yet. Go to the Chat page and send a message to see the agent workflow.")
else:
    st.success(f"📊 {len(logs)} log entries")

    # Display logs in reverse order (newest first)
    for entry in reversed(logs):
        time = entry["time"]
        level = entry["level"]
        message = entry["message"]

        # Color-code by level
        if level == "ERROR":
            st.error(f"`{time}` ❌ {message}")
        elif level == "WARNING":
            st.warning(f"`{time}` ⚠️ {message}")
        else:
            st.text(f"  {time}  ℹ️  {message}")

    st.divider()
    st.caption(
        "💡 These logs show the agent's decision-making process: "
        "tool discovery → Gemini decision → MCP tool call → final response"
    )
