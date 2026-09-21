# MCP Client–Agent Integration

A simple, beginner-friendly project demonstrating how a **Custom AI Agent** uses **Gemini 2.5 Flash** as the LLM and **MCP (Model Context Protocol)** to dynamically discover and call tools — all wrapped in a **Streamlit ChatGPT-like interface**.

---

## 🤖 What Is This Project?

### What is MCP?

**Model Context Protocol (MCP)** is a standard protocol for connecting AI models to external tools.
Think of it like **USB for AI** — any MCP client can connect to any MCP server and use its tools.

### What is an AI Agent?

An **AI Agent** is code that:
1. Receives a user request
2. Decides what action to take (using an LLM)
3. Executes the action
4. Returns the result

Our agent is **custom Python code** — not LangChain, not AutoGen. Just simple functions.

### What is the LLM?

**Gemini 2.5 Flash** by Google — it understands the user's question and decides which tool to use.

---

## 🏗️ Architecture

```
              👤 USER
                │
                ▼
        ┌───────────────┐
        │   Streamlit   │  ← Chat UI (app.py)
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
          Selects a tool
                │
                ▼
        ┌───────────────┐
        │   MCP Client  │  ← Tool bridge (mcp_client.py)
        └───────┬───────┘
                │
          MCP Protocol
                │
        ┌───────┴───────┐
        ▼               ▼
  Utility Server   Calculator Server
  (weather, time)  (arithmetic)
```

---

## 📂 Project Structure

```
MCP-Client-Agent/
│
├── app.py                    # Streamlit chat interface
├── agent.py                  # Custom AI agent (orchestrator)
├── gemini_llm.py             # Gemini LLM connection
├── mcp_client.py             # MCP client (tool discovery + calling)
├── chat_history.py           # In-memory chat management
├── logger.py                 # Simple logging
│
├── servers/
│   ├── utility_server.py     # Weather + Time MCP server
│   └── calculator_server.py  # Calculator MCP server
│
├── pages/
│   ├── 1_Tools.py            # Shows discovered MCP tools
│   ├── 2_Architecture.py     # Architecture explanation
│   └── 3_Logs.py             # Execution logs
│
├── tests/
│   └── test_tools.py         # Simple tests
│
├── .env.example              # API key template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Installation (Windows)

### 1. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key

2. Edit `.env` and paste your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```


### 4. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🧪 Test Queries

Try these in the chat:

| Query | Expected Tool |
|-------|--------------|
| "What is the weather in Pune?" | `get_weather` |
| "What time is it in India?" | `get_current_time` |
| "Calculate 25 * 8 + 10" | `calculate` |
| "Explain what MCP is" | No tool (direct answer) |
| "Calculate 25 * 8 and tell me the time in India" | Multiple tools |

---

## 🔍 Dynamic Tool Discovery

**This is a key feature.** The agent does NOT have a hardcoded list of tools.

Instead:
1. MCP Client connects to each server
2. Calls `session.list_tools()` to ask: "What tools do you have?"
3. Servers respond with their available tools
4. Agent sends these tools to Gemini
5. Gemini picks the right one

**To test:** Add a new tool to `servers/utility_server.py`, restart the app, and it will be discovered automatically.

---

## 🛡️ Fallback Handling

If an MCP server is unavailable:
- The app does NOT crash
- A friendly error message is shown
- Other servers continue working

**To test:** Temporarily rename a server file and try to use its tools.

---

## 🧪 Run Tests

```bash
pytest tests/test_tools.py -v
```

---

## 📊 Execution Flow Example

```
USER: What is the weather in Pune?
  │
  ▼
AGENT: Received request
  │
  ▼
MCP CLIENT: Discovering tools...
  → Found: get_weather, get_current_time, calculate
  │
  ▼
GEMINI: Selected tool → get_weather(city="Pune")
  │
  ▼
MCP CLIENT: Calling get_weather on Utility Server
  │
  ▼
MCP SERVER: Returns demo weather data
  │
  ▼
GEMINI: Generates final answer using weather data
  │
  ▼
STREAMLIT: Shows the answer to the user
```

---


## 📦 Technologies Used

| Technology | Purpose |
|-----------|---------|
| Python 3.11+ | Core language |
| Streamlit | Chat UI |
| Google Gemini 2.5 Flash | LLM (brain) |
| google-genai | Gemini SDK |
| MCP Python SDK v2 | MCP protocol |
| python-dotenv | Environment variables |
| pytest | Testing |
