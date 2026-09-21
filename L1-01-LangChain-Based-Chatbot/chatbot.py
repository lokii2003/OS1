# """
# chatbot.py — Core Chatbot Logic

# Creates the LangChain chain that connects:
#   Prompt Template → Gemini LLM
# Then wraps it with conversation history management.
# """

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.runnables.history import RunnableWithMessageHistory

# from config import GOOGLE_API_KEY, MODEL_NAME
# from prompts import create_prompt_template
# from memory import get_session_history


# def create_chain():
#     """
#     Build the full chatbot chain:

#     1. Create the prompt template (system + history + user input)
#     2. Create the Gemini LLM instance
#     3. Pipe them together: prompt | llm
#     4. Wrap with RunnableWithMessageHistory for auto memory
#     """

#     # Step 1: Prompt template
#     prompt = create_prompt_template()

#     # Step 2: LLM instance
#     llm = ChatGoogleGenerativeAI(
#         model=MODEL_NAME,
#         google_api_key=GOOGLE_API_KEY,
#         # temperature=TEMPERATURE,
#     )

#     # Step 3: Chain — send prompt output into the LLM
#     chain = prompt | llm

#     # Step 4: Wrap with history management
#     chain_with_history = RunnableWithMessageHistory(
#         chain,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="history",
#     )

#     return chain_with_history


# def get_response(user_input: str, session_id: str) -> str:
#     """
#     Send a user message and return the AI response.

#     Args:
#         user_input:  The user's message text.
#         session_id:  Unique ID for this conversation session.

#     Returns:
#         The AI assistant's response as a string.
#     """
#     chain = create_chain()

#     # Config tells RunnableWithMessageHistory which session to use
#     config = {"configurable": {"session_id": session_id}}

#     response = chain.invoke(
#         {"input": user_input},
#         config=config,
#     )

#     content = response.content

#     if isinstance(content, list):
#         return "".join(
#             item.get("text", "")
#             for item in content
#             if isinstance(item, dict)
#         )

#     return content

"""
chatbot.py — Core Chatbot Logic

Prompt Template → Gemini LLM → Conversation Memory
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory

from config import GOOGLE_API_KEY, MODEL_NAME
from prompts import create_prompt_template
from memory import get_session_history


def create_chain():
    """Create the LangChain chatbot chain."""

    # 1. Create prompt
    prompt = create_prompt_template()

    # 2. Create Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
    )

    # 3. Connect prompt → Gemini
    chain = prompt | llm

    # 4. Add conversation memory
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    return chain_with_history


def get_response(user_input: str, session_id: str) -> str:
    """Send user input and return plain text response."""

    chain = create_chain()

    config = {
        "configurable": {
            "session_id": session_id
        }
    }

    response = chain.invoke(
        {"input": user_input},
        config=config,
    )

    # Convert Gemini response to normal text
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text = ""

        for item in content:
            if isinstance(item, dict):
                text += item.get("text", "")

        return text

    return str(content)