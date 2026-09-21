"""
MCP Client
===========
This file is the "connector" between the AI Agent and the MCP Tool Servers.

It uses FastMCP's Client to connect to each MCP server using in-memory
transport (the server and client run in the same Python process).

Think of it like this:
- The Agent (brain) decides WHICH tool to use
- This MCP Client connects to the tool and EXECUTES it
- The tool result comes back through this client

Why do we need this?
Because MCP is a protocol (a standard way for AI agents to talk to tools).
The Client handles all the MCP protocol details for us.
"""

import asyncio
import json
import nest_asyncio
from fastmcp import Client

# Allow asyncio.run() to work inside Streamlit's existing event loop.
# Without this, asyncio.run() throws "RuntimeError: This event loop is already running".
nest_asyncio.apply()

# Import the MCP server instances from our tool files
from tools.sql_tool import sql_server
from tools.image_tool import image_server
from tools.calendar_tool import calendar_server


async def call_sql_tool(tool_name: str, arguments: dict) -> dict:
    """
    Call a tool on the SQL MCP Server.

    This function:
    1. Connects to the SQL MCP server (in-memory, no network needed)
    2. Calls the specified tool with the given arguments
    3. Returns the parsed result

    Args:
        tool_name: Name of the SQL tool to call ("execute_sql" or "list_tables")
        arguments: Dictionary of arguments for the tool

    Returns:
        Parsed JSON dictionary with the tool result
    """
    # Connect to the SQL server using in-memory transport
    # "async with" ensures the connection is properly opened and closed
    async with Client(sql_server) as client:
        # Call the tool and get the result
        result = await client.call_tool(tool_name, arguments)

        # The result contains content blocks — we get the text from the first one
        # Get the content returned by the MCP tool
        result_text = result.content[0].text if result.content else "{}"

        # Parse the JSON string into a Python dictionary
        return json.loads(result_text)


async def call_image_tool(image_path: str, instruction: str) -> dict:
    """
    Call the analyze_image tool on the Image MCP Server.

    This function:
    1. Connects to the Image MCP server
    2. Sends the image path and instruction
    3. Returns the analysis result

    Args:
        image_path: Path to the image file on disk
        instruction: What to analyze about the image

    Returns:
        Parsed JSON dictionary with the analysis result
    """
    async with Client(image_server) as client:
        result = await client.call_tool("analyze_image", {
            "image_path": image_path,
            "instruction": instruction
        })

        # Get the content returned by the MCP tool
        result_text = result.content[0].text if result.content else "{}"

        # Parse the JSON string into a Python dictionary
        return json.loads(result_text)
    

async def call_calendar_tool(tool_name: str, arguments: dict) -> dict:
    """
    Call a tool on the Calendar MCP Server.

    This function:
    1. Connects to the Calendar MCP server
    2. Calls the specified tool (create_event, list_events, etc.)
    3. Returns the result

    Args:
        tool_name: Name of the calendar tool to call
                  ("create_event", "list_events", "update_event", "delete_event")
        arguments: Dictionary of arguments for the tool

    Returns:
        Parsed JSON dictionary with the tool result
    """
    async with Client(calendar_server) as client:
        result = await client.call_tool(tool_name, arguments)

        # Get the content returned by the MCP tool
        result_text = result.content[0].text if result.content else "{}"

        # Parse the JSON string into a Python dictionary
        return json.loads(result_text)


# ---------------------------------------------------------------------------
# Helper function to run async MCP calls from synchronous code.
# Streamlit runs synchronously, so we need this wrapper.
# ---------------------------------------------------------------------------
def run_sql_tool(tool_name: str, arguments: dict) -> dict:
    """Synchronous wrapper for call_sql_tool."""
    return asyncio.run(call_sql_tool(tool_name, arguments))


def run_image_tool(image_path: str, instruction: str) -> dict:
    """Synchronous wrapper for call_image_tool."""
    return asyncio.run(call_image_tool(image_path, instruction))


def run_calendar_tool(tool_name: str, arguments: dict) -> dict:
    """Synchronous wrapper for call_calendar_tool."""
    return asyncio.run(call_calendar_tool(tool_name, arguments))
