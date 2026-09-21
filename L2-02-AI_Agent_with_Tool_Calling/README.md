# 🤖 AI Agent with MCP Tool Calling

An AI Agent built with **Python**, **Google Gemini**, and **MCP (Model Context Protocol)** that can automatically select and call the correct tool based on your question.

---

## 📋 Project Overview

This project demonstrates how to build an AI agent that uses **Gemini's function calling** to automatically route user requests to the right tool:

| User Request | Tool Selected |
|---|---|
| "Show total sales by department" | 🗄️ SQL Database Tool |
| "Describe this image" | 🖼️ Image Analysis Tool |
| "Create a meeting tomorrow at 3 PM" | 📅 Calendar Tool |

**No keyword matching** — Gemini decides which tool to use based on tool descriptions.

---

## ✨ Features

- **Smart Tool Selection**: Gemini AI automatically picks the right tool
- **SQL Database Tool**: Upload CSV files and query them with natural language
- **Image Analysis Tool**: Analyze images using Gemini Vision
- **Calendar Tool**: Create, list, update, and delete calendar events
- **Chat Interface**: Simple Streamlit chat UI
- **Download Results**: Export query results as CSV or Excel
- **Agent Logs**: See exactly what the agent does behind the scenes
- **Error Handling**: Graceful error messages, no crashes

---

## 🏗️ Architecture

```
                    ┌──────────────────┐
                    │      User        │
                    │ Query / File     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  Streamlit UI    │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   AI Agent       │
                    │ Gemini LLM       │
                    │ Intent + Tool    │
                    │ Selection        │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    MCP Client    │
                    └────────┬─────────┘
                             ↓
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ SQL MCP Tool   │  │ Image MCP Tool │  │ Calendar Tool  │
 │                │  │                │  │                │
 │ SQLite DB      │  │ Gemini Vision  │  │ SQLite DB      │
 └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ↓
                    ┌──────────────────┐
                    │   Tool Result    │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   AI Agent       │
                    │ Final Response   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │      User        │
                    └──────────────────┘
```

### How Each Component Maps:

| Component | Role | File |
|---|---|---|
| **Gemini** | Brain — understands intent, picks tools | `agent.py` |
| **MCP Client** | Connector — executes tool calls | `mcp_client.py` |
| **MCP Server** | Tool Provider — hosts the tools | `tools/*.py` |
| **MCP Tool** | Specific Capability — does the work | Functions in `tools/*.py` |
| **SQLite** | Data Storage — stores data & events | `data/*.db` |
| **Streamlit** | User Interface — chat & uploads | `app.py` |

---

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python 3.11+ | Programming language |
| Google Gemini API | AI model (function calling + vision) |
| FastMCP | MCP server/client framework |
| SQLite | Local database |
| Streamlit | Web UI |
| Pandas | Data handling (CSV import) |
| Pillow | Image handling |
| python-dotenv | Environment variables |

---

## 📁 Project Structure

```
AI_Agent_with_Tool_Calling/
│
├── app.py                  ← Streamlit UI (main entry point)
├── agent.py                ← Gemini AI Agent (tool selection)
├── mcp_client.py           ← MCP Client (connects to tools)
├── requirements.txt        ← Python dependencies
├── .env.example            ← API key template
├── README.md               ← This file
│
├── tools/
│   ├── sql_tool.py         ← SQL MCP Server
│   ├── image_tool.py       ← Image Analysis MCP Server
│   └── calendar_tool.py    ← Calendar MCP Server
│
├── data/
│   ├── employees.csv       ← Sample employee data
│   ├── sales.csv           ← Sample sales data
│   ├── database.db         ← SQLite DB (created automatically)
│   └── calendar.db         ← Calendar DB (created automatically)
│
└── uploads/                ← Uploaded images (created automatically)
```


## 🔄 How MCP Works

**MCP (Model Context Protocol)** is a standard protocol for AI agents to communicate with tools.

Think of it like a USB port for AI:
- Any AI agent that "speaks MCP" can use any MCP tool
- The tool doesn't need to know about the specific AI model
- The AI model doesn't need to know the tool's implementation details

### In This Project:

```
1. You type a question
2. Gemini reads the question + tool descriptions
3. Gemini says: "I want to call execute_sql with query='SELECT ...'"
4. MCP Client sends this request to the SQL MCP Server
5. The SQL MCP Server executes the query and returns results
6. The result goes back to Gemini
7. Gemini writes a friendly response
8. You see the answer in the chat
```

### Why MCP Instead of Direct Function Calls?

MCP adds a standard protocol layer. This means:
- Tools can be reused across different AI agents
- Tools can be developed and tested independently
- The protocol handles serialization, validation, and error handling

In this project, we use **in-memory transport** (server and client in the same process) for simplicity. In production, MCP servers can run as separate processes or even on different machines.

---

## 🗄️ SQL Tool

### What It Does
- Upload CSV/Excel files → they become SQLite tables
- Ask questions in natural language → Gemini generates SQL
- Results displayed as tables with download options

### Supported SQL Operations
✅ SELECT, WHERE, GROUP BY, ORDER BY, HAVING, JOIN, UNION
✅ COUNT, SUM, AVG, MIN, MAX, LIMIT

### Blocked Operations (Read-Only Safety)
❌ DROP, DELETE, UPDATE, ALTER, TRUNCATE, INSERT, CREATE

### Example

**User**: "Show total sales by department"

**Gemini generates**:
```sql
SELECT e.department, SUM(s.amount) AS total_sales
FROM employees e
JOIN sales s ON e.employee_id = s.employee_id
GROUP BY e.department
```

**Result**: Table with departments and their total sales.

---

## 🖼️ Image Tool

### What It Does
- Upload an image through the sidebar
- Ask questions about the image
- Uses Gemini Vision for analysis

### Supported Requests
- Describe image
- Identify objects
- Read visible text
- Answer questions about the image

### Example

**User uploads** `product.jpg` and asks: "Describe this image"

**Result**: "The image shows a product placed on a table with a blue background..."

---

## 📅 Calendar Tool

### What It Does
- Create, list, update, and delete calendar events
- Uses a local SQLite database (no Google Calendar API needed)
- Understands relative dates ("tomorrow", "next Monday")

### Example

**User**: "Create a meeting tomorrow at 3 PM called Project Discussion"

**Result**: "Project Discussion has been scheduled for 2026-09-18 at 15:00"

**User**: "What meetings do I have tomorrow?"

**Result**: Table showing all events for tomorrow.

---

## 🎯 Tool Selection

Gemini selects tools using **function calling**, not keyword matching.

Each tool has a description that Gemini reads:

| Tool | Description Summary |
|---|---|
| `execute_sql` | "Use for data queries, employees, sales, counts, averages..." |
| `analyze_image` | "Use for describing images, identifying objects, reading text..." |
| `create_event` | "Use when user wants to schedule meetings or events..." |
| `list_events` | "Use when user asks about schedule or upcoming meetings..." |

Gemini uses these descriptions to decide which tool fits the user's request.

---

## ⚠️ Error Handling

Every tool handles errors gracefully:

| Scenario | Response |
|---|---|
| Table not found | "The requested table 'abc' was not found. Available tables: [...]" |
| Invalid SQL | "SQL execution failed: near 'SELCT': syntax error" |
| Dangerous SQL (DROP, DELETE) | "Only read-only SELECT queries are allowed" |
| No image uploaded | "Please upload an image first" |
| Event not found | "The requested event with ID 'xyz' was not found" |
| API key missing | "Gemini API key not configured. Please set GEMINI_API_KEY in .env" |

---

## 📝 Sample Executions

### SQL Example

```
User Request:
How many employees are in the Data Science department?

Agent Decision:
SQL Database Tool

Tool Called:
execute_sql

Tool Input:
{"query": "SELECT COUNT(*) AS count FROM employees WHERE department = 'Data Science'"}

Tool Output:
{"success": true, "columns": ["count"], "rows": [[5]], "row_count": 1}

Final Response:
There are 5 employees in the Data Science department.
```

### SQL Multiple Files Example

Upload `employees.csv` and `sales.csv`, then ask:

```
User: "Show total sales by department"

→ Agent understands it needs BOTH tables
→ Generates a JOIN + GROUP BY query
→ Returns department totals
```

### Image Example

```
User Request:
Describe this image

Agent Decision:
Image Analysis Tool

Tool Input:
{"instruction": "Describe this image"}

Tool Output:
{"success": true, "analysis": "The image shows a product on a table..."}

Final Response:
The image shows a product placed on a table with a blue background.
```

### Calendar Example

```
User Request:
Create a meeting tomorrow at 3 PM called Project Discussion

Agent Decision:
Calendar Tool

Tool Called:
create_event

Tool Input:
{"title": "Project Discussion", "date": "2026-09-18", "start_time": "15:00", "end_time": "16:00"}

Tool Output:
{"success": true, "event_id": "a1b2c3d4", "message": "Event created successfully"}

Final Response:
Project Discussion has been scheduled for tomorrow (2026-09-18) at 3:00 PM.
```

---

## 📸 Screenshots

> Screenshots will be added after running the application.

---

## 🧪 Test Queries

After starting the app, try these queries to verify all tools work:

| # | Query | Expected Tool | What to Check |
|---|-------|---------------|---------------|
| 1 | "Show all employees" | SQL Database Tool | Returns 20 rows from employees table |
| 2 | "Show total sales by department" | SQL Database Tool | Uses JOIN between employees and sales tables |
| 3 | Upload an image, then ask "Describe this image" | Image Analysis Tool | Returns AI description of the uploaded image |
| 4 | "Create a meeting tomorrow at 3 PM called Team Standup" | Calendar Tool | Creates event with correct date and time |
| 5 | "What events do I have?" | Calendar Tool | Lists all calendar events |

---

## 🔮 Future Improvements

- [ ] Multi-turn conversation memory
- [ ] Google Calendar integration (OAuth)
- [ ] Chart/graph generation from SQL results
- [ ] Audio analysis tool
- [ ] PDF document analysis tool
- [ ] Export chat history
- [ ] User authentication
- [ ] Deploy to cloud (Streamlit Cloud, GCP)

---
