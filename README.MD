# 🤖 AI Projects Repository

This repository contains three AI-based projects developed using Python, Streamlit, Google Gemini, LangChain, and MCP.

---

## 📚 Projects Overview

| Task ID | Project Name | Main Technologies | Port |
| :--- | :--- | :--- | :--- |
| L1-01 | LangChain-Based Chatbot | LangChain, Gemini, Streamlit | `8501` |
| L2-02 | AI Agent with Tool Calling | Gemini, MCP, Tool Calling, Streamlit | `8502` |
| L3-03 | MCP Client–Agent Integration | MCP, FastMCP, Gemini, Streamlit | `8503` |

---

## 📌 Project 1

**Task ID:** L1-01

### LangChain-Based Chatbot

A conversational AI chatbot built using LangChain and Google Gemini. The application provides a simple chat interface and maintains conversation history.

**Technologies:** Python, Streamlit, LangChain, Google Gemini, Python-dotenv

**Project Structure:**

```
L1-01-LangChain-Based-Chatbot/
├── app.py
├── chatbot.py
├── config.py
├── memory.py
└── ...
```

**Run:**

```bash
streamlit run L1-01-LangChain-Based-Chatbot/app.py --server.port 8501
```

**URL:** http://localhost:8501

---

## 📌 Project 2

**Task ID:** L2-02

### AI Agent with Tool Calling

An AI Agent that uses Google Gemini to understand user requests and call appropriate tools to perform different tasks. The project contains tools for calendar operations, image processing, and SQL/data operations.

**Technologies:** Python, Streamlit, Google Gemini, MCP, Tool Calling, Pandas, OpenPyXL

**Project Structure:**

```
L2-02-AI_Agent_with_Tool_Calling/
├── app.py
├── agent.py
├── mcp_client.py
├── tools/
│   ├── __init__.py
│   ├── calendar_tool.py
│   ├── image_tool.py
│   └── sql_tool.py
└── data/
```

**Run:**

```bash
streamlit run L2-02-AI_Agent_with_Tool_Calling/app.py --server.port 8502
```

**URL:** http://localhost:8502

---

## 📌 Project 3

**Task ID:** L3-03

### MCP Client–Agent Integration


An AI Agent that connects to MCP servers, discovers available tools, and uses those tools according to the user's request. The project includes a Calculator Server, Utility Server, MCP Client, and Gemini integration with tool discovery.

**Technologies:** Python, Streamlit, Google Gemini, MCP, FastMCP, MCP Client

**Project Structure:**

```
L3-03-MCP-Client-Agent/
├── app.py
├── agent.py
├── chat_history.py
├── gemini_llm.py
├── logger.py
├── mcp_client.py
├── pages/
│   ├── 1_Tools.py
│   ├── 2_Architecture.py
│   └── 3_Logs.py
├── servers/
│   ├── calculator_server.py
│   └── utility_server.py
└── tests/
    └── test_tools.py
```

**Run:**

```bash
streamlit run L3-03-MCP-Client-Agent/app.py --server.port 8503
```

**URL:** http://localhost:8503

---

## 📂 Repository Structure

```
OS3/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── L1-01-LangChain-Based-Chatbot/
├── L2-02-AI_Agent_with_Tool_Calling/
└── L3-03-MCP-Client-Agent/
```

All three projects share one common `.venv`, one `requirements.txt`, one `.env`, and one `.gitignore`.

---

## ⚙️ Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/lokii2003/OS3.git
cd OS3
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should show:

```
(.venv) PS C:\...\OS3>
```

### 4. Install Requirements

```bash
pip install -r requirements.txt
```

**Dependencies included:**

```
streamlit
google-genai
mcp[cli]
fastmcp
langchain
langchain-core
langchain-google-genai
python-dotenv
pytest
pandas
Pillow
openpyxl
nest-asyncio
```

---

## 🔐 API Key Setup

### 1. Create `.env` from `.env.example`

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

### 2. Edit `.env` and add your API key

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

MODEL_NAME=gemini-3.6-flash
GEMINI_MODEL=gemini-3.6-flash
TEMPERATURE=0.7
```

Replace `your_google_api_key_here` and `your_gemini_api_key_here` with your actual Gemini API key.

### 3. Save the `.env` file in the root folder

```
OS3/
├── .env           ← your private keys (never push to GitHub)
├── .env.example   ← template for other users
├── requirements.txt
└── ...
```

> ⚠️ **Do not upload `.env` to GitHub.** It contains private API credentials. Use `.env.example` as the template for other users.

---

## ▶️ Run All Three Projects

All three projects can run simultaneously because each uses a different Streamlit port. Open three separate terminals and activate the same environment in each:

```powershell
.\.venv\Scripts\Activate.ps1
```

**Terminal 1 — L1-01:**

```bash
streamlit run L1-01-LangChain-Based-Chatbot/app.py --server.port 8501
```

**Terminal 2 — L2-02:**

```bash
streamlit run L2-02-AI_Agent_with_Tool_Calling/app.py --server.port 8502
```

**Terminal 3 — L3-03:**

```bash
streamlit run L3-03-MCP-Client-Agent/app.py --server.port 8503
```

---

## 🌐 Application Ports

| Task ID | Project | Port | URL |
| :--- | :--- | :--- | :--- |
| L1-01 | LangChain-Based Chatbot | `8501` | http://localhost:8501 |
| L2-02 | AI Agent with Tool Calling | `8502` | http://localhost:8502 |
| L3-03 | MCP Client Agent | `8503` | http://localhost:8503 |

To stop a running project, press `Ctrl + C` in its terminal.

---

## 🔒 Security

- Never commit API keys to GitHub.
- Never upload `.env` or `.venv/`.
- Keep personal credentials private.
- Use `.env.example` as the configuration template.
- Keep generated files and local databases excluded via `.gitignore`.

---

## 👨‍💻 Author

**Lokesh Kumawat**

AI / ML · Generative AI · LangChain · MCP · Python