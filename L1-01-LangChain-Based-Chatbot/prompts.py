"""
prompts.py — System Prompt and Prompt Template

Defines the chatbot's personality and creates the
LangChain prompt template with conversation history support.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# System prompt — defines how the chatbot behaves
SYSTEM_PROMPT = """You are a helpful and professional AI assistant.

- Answer clearly and accurately.
- Maintain conversation context across messages.
- Use previous messages when answering follow-up questions.
- If you do not know something, say so honestly.
- Keep answers concise unless the user asks for more detail."""


def create_prompt_template():
    """
    Create a ChatPromptTemplate with:
    1. System message — sets chatbot behavior
    2. History placeholder — injects past conversation messages
    3. Human message — the user's current input
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    return prompt
