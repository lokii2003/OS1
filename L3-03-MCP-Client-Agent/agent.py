"""
=============================================================
CUSTOM AI AGENT
=============================================================
Purpose:
    This is the HEART of the project — the orchestrator.
    It connects everything together:
    User → Gemini → MCP Client → MCP Server → Tool → Gemini → User

Why we need it:
    The agent is our custom Python code that controls the workflow.
    It is NOT a framework like LangChain or AutoGen.
    It's simple Python functions that we wrote ourselves.

How it connects:
    - app.py (Streamlit) calls process_message()
    - Agent calls mcp_client to discover tools
    - Agent calls gemini_llm to get tool decisions
    - Agent calls mcp_client to execute tools
    - Agent calls gemini_llm to get final answers
    - Agent returns the final response to Streamlit

Workflow:
    1. User sends message
    2. Agent discovers available MCP tools
    3. Agent sends message + tools to Gemini
    4. Gemini decides: answer directly OR call a tool
    5. If tool needed → Agent calls MCP tool → sends result to Gemini
    6. Agent returns final answer to Streamlit
=============================================================
"""

import asyncio
import mcp_client                                        # Our MCP client module
import gemini_llm                                        # Our Gemini module
from logger import log

# Maximum tool calls per request (prevents infinite loops)
MAX_TOOL_CALLS = 3


async def _discover_tools_async():
    """Discover tools from all MCP servers (async)."""
    return await mcp_client.discover_tools()


async def _call_tool_async(tool_name, arguments, server_id):
    """Call an MCP tool (async)."""
    return await mcp_client.call_tool(tool_name, arguments, server_id)


def process_message(user_message: str, chat_messages: list = None):
    """
    Process a user message through the full agent workflow.

    This is the main function that Streamlit calls.

    Args:
        user_message: What the user typed
        chat_messages: Previous messages in the conversation

    Returns:
        dict: {
            "response": "Final answer text",
            "tool_executions": [
                {
                    "tool_name": "get_weather",
                    "server_name": "Utility Server",
                    "arguments": {"city": "Pune"},
                    "result": "Temperature: 28°C...",
                    "success": True
                }
            ]
        }
    """
    log(f"📩 User request received: {user_message[:80]}...")

    tool_executions = []  # Track all tool calls for the UI

    # ----- STEP 1: Discover available MCP tools -----
    log("Step 1: Discovering MCP tools...")
    try:
        discovery = asyncio.run(_discover_tools_async())
        tools = discovery["tools"]
        servers = discovery["servers"]
        log(f"Step 1 complete: {len(tools)} tools found")
    except Exception as e:
        log(f"Tool discovery failed: {e}", level="ERROR")
        tools = []
        servers = {}

    # Build a lookup: tool_name → server_id
    # This tells us which server owns each tool
    tool_server_map = {t["name"]: t["server_id"] for t in tools}
    tool_name_to_info = {t["name"]: t for t in tools}

    # ----- STEP 2: Ask Gemini what to do -----
    log("Step 2: Asking Gemini to decide...")
    gemini_response = gemini_llm.ask_gemini(user_message, tools, chat_messages)

    # ----- STEP 3: Handle Gemini's decision -----
    if gemini_response["type"] == "text":
        # Gemini answered directly — no tool needed
        log("Step 3: Gemini answered directly (no tool call)")
        return {
            "response": gemini_response["text"],
            "tool_executions": [],
        }

    # Gemini wants to call one or more tools
    tool_calls = gemini_response["tool_calls"]
    log(f"Step 3: Gemini requested {len(tool_calls)} tool call(s)")

    # ----- STEP 4: Execute tool calls via MCP -----
    final_response = ""

    for i, tc in enumerate(tool_calls[:MAX_TOOL_CALLS]):
        tool_name = tc["name"]
        tool_args = tc["args"]

        log(f"Step 4.{i+1}: Calling MCP tool '{tool_name}'")

        # Find which server has this tool
        server_id = tool_server_map.get(tool_name)
        server_name = tool_name_to_info.get(tool_name, {}).get("server_name", "Unknown")

        if not server_id:
            # Tool not found in any server
            log(f"Tool '{tool_name}' not found in any server", level="WARNING")
            tool_executions.append({
                "tool_name": tool_name,
                "server_name": "Unknown",
                "arguments": tool_args,
                "result": f"⚠️ Tool '{tool_name}' not found.",
                "success": False,
            })
            continue

        # Call the tool via MCP
        try:
            result = asyncio.run(_call_tool_async(tool_name, tool_args, server_id))
        except Exception as e:
            log(f"MCP tool call failed: {e}", level="ERROR")
            result = {"success": False, "result": None, "error": str(e)}

        tool_executions.append({
            "tool_name": tool_name,
            "server_name": server_name,
            "arguments": tool_args,
            "result": result.get("result", result.get("error", "No result")),
            "success": result.get("success", False),
        })

        if result["success"]:
            # ----- STEP 5: Send tool result to Gemini for final answer -----
            log("Step 5: Sending tool result to Gemini for final answer")
            final_response = gemini_llm.ask_gemini_with_tool_result(
                user_message=user_message,
                tool_name=tool_name,
                tool_args=tool_args,
                tool_result=result["result"],
                mcp_tools=tools,
                chat_messages=chat_messages,
                model_content=gemini_response.get("model_content"),
            )
        else:
            # Tool failed — provide a friendly error
            error_msg = result.get("error", "Unknown error")
            log(f"Tool '{tool_name}' failed: {error_msg}", level="ERROR")
            final_response = (
                f"⚠️ The tool '{tool_name}' on {server_name} encountered an error:\n"
                f"{error_msg}\n\n"
                f"The MCP server may be unavailable. Please try again later."
            )

    # If we had multiple tool calls, combine results
    if not final_response:
        final_response = "I tried to process your request but couldn't get a complete result."

    log("✅ Agent workflow complete")

    return {
        "response": final_response,
        "tool_executions": tool_executions,
    }


def get_server_status():
    """
    Get the current status of all MCP servers.
    Used by the Streamlit sidebar to show connection status.

    Returns:
        dict: Server status from MCP discovery
    """
    try:
        discovery = asyncio.run(_discover_tools_async())
        return discovery["servers"]
    except Exception as e:
        log(f"Server status check failed: {e}", level="ERROR")
        # Return all servers as disconnected
        return {
            sid: {"name": cfg["name"], "status": "disconnected", "tool_count": 0, "error": str(e)}
            for sid, cfg in mcp_client.SERVER_CONFIGS.items()
        }


def get_discovered_tools():
    """
    Get all dynamically discovered tools.
    Used by the Tools page to display available tools.

    Returns:
        list: List of tool dicts from MCP discovery
    """
    try:
        discovery = asyncio.run(_discover_tools_async())
        return discovery["tools"]
    except Exception as e:
        log(f"Tool discovery failed: {e}", level="ERROR")
        return []
