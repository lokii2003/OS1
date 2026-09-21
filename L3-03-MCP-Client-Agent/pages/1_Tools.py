"""
=============================================================
TOOLS PAGE
=============================================================
Purpose:
    Displays all MCP tools dynamically discovered from the servers.
    This page does NOT hardcode tool names — it reads them at runtime.

Why we need it:
    Demonstrates dynamic tool discovery — the core MCP feature.
    If you add a new tool to an MCP server, it appears here automatically.
=============================================================
"""

import streamlit as st
import agent

st.set_page_config(page_title="MCP Tools", page_icon="🔧", layout="wide")

st.header("🔧 Available MCP Tools")
st.caption("These tools are dynamically discovered from MCP servers at runtime")

# Discover tools from MCP servers
with st.spinner("Discovering tools from MCP servers..."):
    tools = agent.get_discovered_tools()

if not tools:
    st.warning("⚠️ No tools discovered. Make sure MCP servers are available.")
    st.info("The servers are started automatically when needed, but there may be a connection issue.")
else:
    st.success(f"✅ {len(tools)} tools discovered from MCP servers")
    st.divider()

    # Display each tool as a card
    for tool in tools:
        with st.container(border=True):
            # Tool name and server
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"🔹 `{tool['name']}`")
            with col2:
                st.caption(f"📡 {tool['server_name']}")

            # Description
            st.markdown(f"**Description:** {tool['description']}")

            # Input parameters
            schema = tool.get("input_schema", {})
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            if properties:
                st.markdown("**Input Parameters:**")
                for param_name, param_info in properties.items():
                    is_required = "✅ Required" if param_name in required else "Optional"
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    st.markdown(
                        f"- `{param_name}` ({param_type}) — {param_desc} [{is_required}]"
                    )

    st.divider()
    st.info(
        "💡 **Dynamic Discovery:** These tools are NOT hardcoded. "
        "If you add a new tool to an MCP server, it will appear here automatically "
        "after a refresh."
    )
