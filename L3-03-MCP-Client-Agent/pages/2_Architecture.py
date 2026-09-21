"""
=============================================================
ARCHITECTURE PAGE
=============================================================
Purpose:
    Visual explanation of the project architecture.
    Helps understand how all components connect together.
=============================================================
"""

import streamlit as st

st.set_page_config(page_title="Architecture", page_icon="🏗️", layout="wide")

st.header("🏗️ Project Architecture")
st.caption("How all the components connect together")

# -----------------------------------------------
# Architecture Diagram
# -----------------------------------------------
st.subheader("📐 System Flow")

st.code("""
              👤 USER
                │
                ▼
        ┌───────────────┐
        │   Streamlit   │  ← Chat interface (app.py)
        │   Chat UI     │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │  Custom AI    │  ← Orchestrator (agent.py)
        │    Agent      │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Gemini 2.5    │  ← LLM brain (gemini_llm.py)
        │    Flash      │
        └───────┬───────┘
                │
          Decides tool
                │
                ▼
        ┌───────────────┐
        │   MCP Client  │  ← Tool discovery & calling (mcp_client.py)
        └───────┬───────┘
                │
          MCP Protocol (stdio)
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
  ┌──────────┐   ┌──────────┐
  │ Utility  │   │Calculator│
  │ Server   │   │ Server   │
  └────┬─────┘   └────┬─────┘
       │               │
       ▼               ▼
  get_weather      calculate
  get_current_time
       │               │
       ▼               ▼
    Result           Result
       │               │
       └───────┬───────┘
               │
               ▼
        ┌───────────────┐
        │    Gemini     │  ← Creates final answer
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │   Streamlit   │  ← Shows answer to user
        └───────────────┘
""", language=None)

st.divider()

# -----------------------------------------------
# Component Explanations
# -----------------------------------------------
st.subheader("📦 Components Explained")

# Component 1: Streamlit
with st.container(border=True):
    st.markdown("### 🖥️ Streamlit (Frontend)")
    st.markdown("""
    **What:** The chat interface the user sees and types in.

    **Why:** Provides a ChatGPT-like experience. Shows messages,
    tool execution details, and server status.

    **File:** `app.py`
    """)

# Component 2: AI Agent
with st.container(border=True):
    st.markdown("### 🤖 Custom AI Agent (Orchestrator)")
    st.markdown("""
    **What:** Python code that controls the entire workflow.

    **Why:** This is what makes it an "agent" — it decides what to do step by step:
    1. Discover tools from MCP servers
    2. Ask Gemini what tool to use
    3. Call the tool via MCP
    4. Send the result back to Gemini
    5. Return the final answer

    **File:** `agent.py`

    **Important:** This is NOT LangChain or any framework. It's our own simple Python code.
    """)

# Component 3: Gemini
with st.container(border=True):
    st.markdown("### 🧠 Gemini 2.5 Flash (LLM)")
    st.markdown("""
    **What:** Google's large language model — the "brain" of the agent.

    **Why:** It understands the user's question and decides which tool to use.
    After the tool runs, Gemini creates a natural language answer using the result.

    **File:** `gemini_llm.py`

    **Key concept:** We disable automatic function calling so our agent controls the flow.
    """)

# Component 4: MCP Client
with st.container(border=True):
    st.markdown("### 🔌 MCP Client")
    st.markdown("""
    **What:** Connects to MCP servers, discovers tools, and calls them.

    **Why:** This is the "bridge" between our agent and the tool servers.
    It uses the MCP protocol to communicate.

    **File:** `mcp_client.py`

    **Key operations:**
    - `session.list_tools()` → Discover what tools a server has
    - `session.call_tool()` → Execute a specific tool
    """)

# Component 5: MCP Servers
with st.container(border=True):
    st.markdown("### ⚙️ MCP Servers (Tool Providers)")
    st.markdown("""
    **What:** Servers that provide tools over the MCP protocol.

    **Why:** They expose functionality (weather, calculator) as standardized tools
    that any MCP client can discover and use.

    **Files:**
    - `servers/utility_server.py` — Weather + Time tools
    - `servers/calculator_server.py` — Calculator tool

    **Transport:** stdio (stdin/stdout communication)
    """)

st.divider()

# -----------------------------------------------
# Key Concepts
# -----------------------------------------------
st.subheader("📚 Key Concepts")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### 🔍 Dynamic Tool Discovery")
        st.markdown("""
        Tools are NOT hardcoded in the agent.
        The MCP client asks each server: "What tools do you have?"
        If you add a new tool to a server, the agent discovers it automatically.
        """)

    with st.container(border=True):
        st.markdown("#### 🛡️ Fallback Handling")
        st.markdown("""
        If an MCP server is down, the agent shows a friendly error instead of crashing.
        The application continues running.
        """)

with col2:
    with st.container(border=True):
        st.markdown("#### 🔧 Tool Calling Flow")
        st.markdown("""
        1. Gemini says: "Use get_weather with city=Pune"
        2. Agent tells MCP Client to call it
        3. MCP Client connects to the right server
        4. Tool runs and returns a result
        5. Agent sends result back to Gemini
        6. Gemini creates a nice answer
        """)

    with st.container(border=True):
        st.markdown("#### 📡 MCP Protocol")
        st.markdown("""
        **Model Context Protocol** — a standard for AI tools.
        Think of it like USB for AI: any client can connect to any server.
        We use **stdio transport** (stdin/stdout) for simplicity.
        """)
