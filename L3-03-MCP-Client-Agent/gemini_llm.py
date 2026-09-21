"""
=============================================================
GEMINI LLM MODULE
=============================================================
Purpose:
    Connects to Google's Gemini 2.5 Flash model.
    Handles sending messages, tool declarations, and receiving
    tool call decisions from Gemini.

Why we need it:
    Gemini is the "brain" of our agent. It:
    1. Understands user questions
    2. Decides which MCP tool to use (or answers directly)
    3. Creates a final answer after receiving tool results

How it connects:
    - agent.py calls ask_gemini() with the user question + available tools
    - Gemini returns either a direct answer or a tool call request
    - agent.py calls ask_gemini_with_tool_result() to get the final answer

Key SDK:
    google-genai (not the old google-generativeai)
=============================================================
"""

import os
from dotenv import load_dotenv                           # Reads .env file
from google import genai                                 # Google Gemini SDK
from google.genai import types                           # Gemini types (Tool, FunctionDeclaration, etc.)
from logger import log

# Load environment variables from .env file
load_dotenv()

# --- Initialize Gemini Client ---
# The API key comes from .env, never hardcoded
_api_key = os.getenv("GEMINI_API_KEY")
_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not _api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")

client = genai.Client(api_key=_api_key)  # Create the Gemini client


def mcp_tools_to_gemini_declarations(mcp_tools: list) -> types.Tool:
    """
    Convert MCP tool definitions → Gemini FunctionDeclarations.

    MCP tools have their own schema format.
    Gemini needs FunctionDeclaration objects.
    This function translates between the two.

    Args:
        mcp_tools: List of tool dicts from mcp_client.discover_tools()

    Returns:
        A Gemini Tool object containing all function declarations
    """
    declarations = []

    for tool in mcp_tools:
        # Build the JSON schema for Gemini from the MCP tool's input schema
        schema = tool.get("input_schema", {})

        # Extract properties and required fields from MCP schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Build a clean parameter schema for Gemini
        param_properties = {}
        for prop_name, prop_info in properties.items():
            param_properties[prop_name] = {
                "type": prop_info.get("type", "string"),
                "description": prop_info.get("description", prop_name),
            }

        # Create Gemini FunctionDeclaration
        func_decl = types.FunctionDeclaration(
            name=tool["name"],
            description=tool.get("description", "No description"),
            parameters_json_schema={
                "type": "object",
                "properties": param_properties,
                "required": required,
            } if param_properties else None,
        )
        declarations.append(func_decl)

    # Wrap all declarations in a single Tool object
    return types.Tool(function_declarations=declarations)


def ask_gemini(user_message: str, mcp_tools: list, chat_messages: list = None):
    """
    Send a user message to Gemini along with available MCP tools.

    Gemini will either:
    - Answer directly (no tool needed)
    - Request a tool call (returns function_calls)

    Args:
        user_message: The user's question
        mcp_tools: Available tools from MCP discovery
        chat_messages: Previous conversation messages for context

    Returns:
        dict: {
            "type": "text" or "tool_call",
            "text": "direct answer" (if type is "text"),
            "tool_calls": [{"name": ..., "args": {...}}] (if type is "tool_call")
        }
    """
    log(f"Sending request to Gemini ({_model})")

    try:
        # Convert MCP tools to Gemini format
        gemini_tool = mcp_tools_to_gemini_declarations(mcp_tools)

        # Build conversation contents for context
        contents = []

        # Add previous messages for context (keep last 10 for efficiency)
        if chat_messages:
            for msg in chat_messages[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

        # Add the current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        ))

        # Call Gemini with automatic function calling DISABLED
        # We disable it so OUR agent controls the tool execution
        response = client.models.generate_content(
            model=_model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[gemini_tool] if mcp_tools else [],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True  # We handle tool calls ourselves
                ),
            ),
        )

        # Check if Gemini wants to call a tool
        if response.function_calls:
            tool_calls = []
            for fc in response.function_calls:
                tool_calls.append({
                    "name": fc.name,
                    "args": dict(fc.args) if fc.args else {},
                })
                log(f"Gemini selected tool: {fc.name}")

            return {
                "type": "tool_call",
                "tool_calls": tool_calls,
                "model_content": response.candidates[0].content
                }

        # No tool needed — Gemini answered directly
        log("Gemini answered directly (no tool needed)")
        return {"type": "text", "text": response.text or "I couldn't generate a response."}

    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        log(error_msg, level="ERROR")
        return {"type": "text", "text": f"⚠️ {error_msg}"}


def ask_gemini_with_tool_result(
    user_message: str,
    tool_name: str,
    tool_args: dict,
    tool_result: str,
    mcp_tools: list,
    chat_messages: list = None,
    model_content=None,
):
    """
    Send the tool result back to Gemini to generate a final answer.

    Flow:
    1. User asked a question
    2. Gemini requested a tool call
    3. We called the tool via MCP and got a result
    4. NOW we send that result back to Gemini
    5. Gemini creates a nice final answer using the tool result

    Args:
        user_message: Original user question
        tool_name: Name of the tool that was called
        tool_args: Arguments that were sent to the tool
        tool_result: The result returned by the MCP tool
        mcp_tools: Available tools (for Gemini config)
        chat_messages: Previous conversation messages
        model_content: The raw model content from the first response

    Returns:
        str: Gemini's final answer incorporating the tool result
    """
    log(f"Sending tool result back to Gemini for final answer")

    try:
        gemini_tool = mcp_tools_to_gemini_declarations(mcp_tools)

        # Build the conversation:
        # 1. Previous context
        # 2. User message
        # 3. Model's tool call request
        # 4. Tool result (function response)
        contents = []

        # Add chat history for context
        if chat_messages:
            for msg in chat_messages[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

        # User's message
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        ))

        

        # Model's original tool call
        # Keeps Gemini's thought_signature
        contents.append(model_content)

        # Tool result (what the MCP tool returned)
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name=tool_name,
                response={"result": tool_result},
            )]
        ))

        # Ask Gemini to generate the final answer
        response = client.models.generate_content(
            model=_model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[gemini_tool] if mcp_tools else [],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

        log("✅ Final response generated by Gemini")
        return response.text or "I processed the tool result but couldn't generate a response."

    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        log(error_msg, level="ERROR")
        return f"⚠️ {error_msg}\n\nTool result was: {tool_result}"
