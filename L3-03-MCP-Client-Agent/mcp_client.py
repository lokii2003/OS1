"""
=============================================================
MCP CLIENT
=============================================================
Purpose:
    Connects to MCP servers, discovers tools, and calls them.
    This is the bridge between our AI Agent and the MCP servers.

Why we need it:
    The MCP client is what makes "dynamic tool discovery" possible.
    Instead of hardcoding tool names, we ASK the servers what
    tools they have at runtime.

How it connects:
    - agent.py calls discover_tools() to get available tools
    - agent.py calls call_tool() to execute a specific tool
    - This module connects to MCP servers via stdio transport

Key MCP SDK v2 APIs used:
    - StdioServerParameters: defines how to start a server
    - stdio_client: creates a connection to a server via stdin/stdout
    - ClientSession: manages the MCP protocol session
    - session.list_tools(): discovers available tools
    - session.call_tool(): executes a tool
=============================================================
"""

import os
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters    # MCP protocol classes
from mcp.client.stdio import stdio_client               # stdio transport
from logger import log
from pathlib import Path

# Get the actual project folder
BASE_DIR = Path(__file__).resolve().parent
SERVERS_DIR = BASE_DIR / "servers"

# -----------------------------------------------
# SERVER CONFIGURATION
# -----------------------------------------------
# Define which MCP servers to connect to.
# Each server runs as a subprocess via stdio transport.
# -----------------------------------------------

SERVER_CONFIGS = {
    "utility": {
        "name": "Utility Server",
        "params": StdioServerParameters(
            command=sys.executable,                        # Use the current Python interpreter
            args=[str(SERVERS_DIR / "utility_server.py")],  # Path to server script
        )
    },
    "calculator": {
        "name": "Calculator Server",
        "params": StdioServerParameters(
            command=sys.executable,
            args=[str(SERVERS_DIR / "calculator_server.py")],
        )
    }
}


async def discover_tools():
    """
    Connect to ALL MCP servers and discover their tools.

    Returns:
        dict: {
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Returns demo weather...",
                    "input_schema": {...},
                    "server_id": "utility",
                    "server_name": "Utility Server"
                },
                ...
            ],
            "servers": {
                "utility":    {"name": "Utility Server",    "status": "connected", "tool_count": 2},
                "calculator": {"name": "Calculator Server", "status": "connected", "tool_count": 1}
            }
        }
    """
    all_tools = []
    server_status = {}

    log("Discovering MCP tools from all servers...")

    for server_id, config in SERVER_CONFIGS.items():
        server_name = config["name"]
        try:
            log(f"Connecting to {server_name}...")

            # Connect to the MCP server via stdio
            async with stdio_client(config["params"]) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the MCP connection (required handshake)
                    await session.initialize()

                    # Ask the server: "What tools do you have?"
                    tools_result = await session.list_tools()

                    # Store each discovered tool with its server info
                    for tool in tools_result.tools:
                        all_tools.append({
                            "name": tool.name,
                            "description": tool.description or "No description",
                            "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                            "server_id": server_id,
                            "server_name": server_name,
                        })

                    tool_count = len(tools_result.tools)
                    server_status[server_id] = {
                        "name": server_name,
                        "status": "connected",
                        "tool_count": tool_count,
                    }
                    log(f"✅ {server_name}: {tool_count} tools discovered")

        except Exception as e:
            # Server is unavailable — log it but don't crash
            log(f"❌ {server_name}: Connection failed — {str(e)}", level="ERROR")
            server_status[server_id] = {
                "name": server_name,
                "status": "disconnected",
                "tool_count": 0,
                "error": str(e),
            }

    log(f"Total tools discovered: {len(all_tools)}")
    return {"tools": all_tools, "servers": server_status}


async def call_tool(tool_name: str, arguments: dict, server_id: str):
    """
    Call a specific MCP tool on a specific server.

    Args:
        tool_name: Name of the tool to call (e.g., "get_weather")
        arguments: Arguments to pass to the tool (e.g., {"city": "Pune"})
        server_id: Which server to connect to (e.g., "utility")

    Returns:
        dict: {"success": True/False, "result": "...", "error": "..."}
    """
    config = SERVER_CONFIGS.get(server_id)
    if not config:
        return {"success": False, "result": None, "error": f"Unknown server: {server_id}"}

    server_name = config["name"]
    log(f"Calling tool '{tool_name}' on {server_name} with args: {arguments}")

    try:
        # Connect to the MCP server
        async with stdio_client(config["params"]) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the tool through MCP protocol
                result = await session.call_tool(tool_name, arguments)

                # Extract text from the result
                # MCP returns content as a list of content blocks
                result_text = ""
                for content_block in result.content:
                    if hasattr(content_block, 'text'):
                        result_text += content_block.text

                log(f"✅ Tool '{tool_name}' executed successfully")
                return {"success": True, "result": result_text, "error": None}

    except Exception as e:
        error_msg = f"Tool call failed: {str(e)}"
        log(f"❌ {error_msg}", level="ERROR")
        return {"success": False, "result": None, "error": error_msg}
