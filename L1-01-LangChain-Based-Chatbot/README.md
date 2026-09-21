# 🤖 LangChain-Based Conversational Chatbot

A simple conversational AI chatbot built with **LangChain**, **Google Gemini**, and **Streamlit**. Demonstrates LLM integration, prompt engineering, conversation memory, and modular Python architecture.

---

## Project Overview

This project is a multi-turn conversational chatbot that remembers context within a session. It uses LangChain to orchestrate prompt templates, conversation history, and LLM calls, with a clean Streamlit frontend.

---

## Features

- ✅ Google Gemini LLM integration via LangChain
- ✅ Structured prompt templates with system instructions
- ✅ Multi-turn conversation memory (remembers previous messages)
- ✅ Simple Streamlit chat interface
- ✅ Environment-based configuration (`.env`)
- ✅ Basic error handling
- ✅ Modular, easy-to-read code

---

## Architecture
                    ┌─────────────────────────┐
                    │         User            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Streamlit Frontend   │
                    │         app.py          │
                    │                         │
                    │  • Chat Interface       │
                    │  • User Input           │
                    │  • Chat Display         │
                    │  • Clear Chat           │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Chatbot Logic       │
                    │       chatbot.py        │
                    │                         │
                    │  • Create LLM           │
                    │  • Create Chain         │
                    │  • Process Response     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │  Prompt Template │      │ Conversation     │
          │    prompts.py    │      │     Memory       │
          │                  │      │    memory.py     │
          │ • System Prompt  │      │                  │
          │ • User Input     │      │ • Chat History   │
          │ • History        │      │ • Session ID     │
          └────────┬─────────┘      └────────┬─────────┘
                   │                         │
                   └───────────┬─────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │      LangChain Chain    │
                    │                         │
                    │  Prompt → LLM → Output  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Google Gemini       │
                    │          LLM            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      AI Response        │
                    │                         │
                    │  Response Processing    │
                    │  + Memory Update        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Streamlit Frontend   │
                    │       app.py            │
                    └─────────────────────────┘
```

## Project Structure

```
LangChain-Based-Chatbot/
│
├── app.py              # Streamlit frontend
├── chatbot.py          # LangChain chain and response logic
├── config.py           # Environment configuration
├── prompts.py          # System prompt and prompt template
├── memory.py           # Conversation history management
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```


## Sample Conversation

```
User: My name is Lokesh.

AI: Nice to meet you, Lokesh! How can I help you today?

User: What is my name?

AI: Your name is Lokesh.

User: Tell me a fun fact.

AI: Here's a fun fact: Honey never spoils. Archaeologists have found 3,000-year-old
    honey in Egyptian tombs that was still perfectly edible!

User: Summarize our conversation.

AI: Sure! You introduced yourself as Lokesh, asked me to recall your name,
    and then asked for a fun fact about honey.
```

---

## Design Decisions

| Decision | Reason |
|---|---|
| **LangChain** | Provides structured prompt templates, chain composition, and memory management out of the box |
| **Google Gemini** | Free tier available, fast responses, excellent for conversational AI |
| **Prompt Templates** | Separate prompt logic from code, making it easy to modify chatbot behavior |
| **Conversation Memory** | Enables multi-turn conversations where the AI remembers context |
| **Streamlit** | Fastest way to build a Python-based chat UI with minimal code |
| **`.env` file** | Keeps API keys out of source code for security |

---

## Future Improvements

- 📁 Persistent chat history (save conversations to a database)
- 📄 RAG — Retrieval Augmented Generation (chat with documents)
- 🛠️ Tool calling (let the AI use external tools/APIs)
- 🔐 User authentication
- 🐳 Docker containerization for deployment

