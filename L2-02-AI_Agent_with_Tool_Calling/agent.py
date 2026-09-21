"""
Gemini AI Agent
================
This is the "brain" of the application.

It uses Google's Gemini model with FUNCTION CALLING to:
1. Understand what the user wants
2. Automatically decide which MCP tool to use
3. Generate the right arguments for that tool
4. Send the tool result back to Gemini for a final natural language response

IMPORTANT: Gemini decides the tool using its built-in function calling ability.
We do NOT use keyword matching like `if "image" in query`.
Instead, we give Gemini descriptions of each tool, and it picks the right one.
"""

import os
import json
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our MCP client functions
from mcp_client import run_sql_tool, run_image_tool, run_calendar_tool

# Load the API key from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Set up the Gemini client.
# We use google-genai SDK which is Google's official Python SDK.
# We create the client on-demand (not at import time) so the app
# doesn't crash if the API key is missing.
# ---------------------------------------------------------------------------

# The model we use — gemini-3.6-flash is fast and supports function calling
MODEL_NAME = "gemini-3.6-flash"


def get_gemini_client():
    """
    Create and return a Gemini client.
    Returns None if the API key is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Define the tools that Gemini can choose from.
# These are "function declarations" — they tell Gemini what tools are available,
# what each tool does, and what arguments it needs.
# Gemini reads these descriptions to decide which tool to call.
# ---------------------------------------------------------------------------

# Tool 1: SQL Database Tool
execute_sql_declaration = types.FunctionDeclaration(
    name="execute_sql",
    description=(
        "Execute a read-only SQL query against the SQLite database. "
        "Use this tool when the user asks questions about data, employees, sales, "
        "departments, counts, averages, totals, sorting, filtering, grouping, "
        "joining tables, or any data analysis. "
        "Generate appropriate SQL (SELECT only) based on the user's question."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="The SQL SELECT query to execute against SQLite database."
            )
        },
        required=["query"]
    )
)

# Tool 1b: List Tables (helps the agent know what data is available)
list_tables_declaration = types.FunctionDeclaration(
    name="list_tables",
    description=(
        "List all tables available in the database with their column information. "
        "Use this when you need to know what tables exist or understand the "
        "database structure before writing a SQL query."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
        required=[]
    )
)

# Tool 2: Image Analysis Tool
analyze_image_declaration = types.FunctionDeclaration(
    name="analyze_image",
    description=(
        "Analyze an uploaded image using AI vision. "
        "Use this tool when the user asks to describe an image, identify objects, "
        "read text in an image, or answer questions about an uploaded image. "
        "Requires an image to be uploaded first."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "instruction": types.Schema(
                type=types.Type.STRING,
                description="What to analyze about the image (e.g., 'Describe this image')."
            )
        },
        required=["instruction"]
    )
)

# Tool 3: Calendar Tools
create_event_declaration = types.FunctionDeclaration(
    name="create_event",
    description=(
        "Create a new calendar event or meeting. "
        "Use this when the user wants to schedule something."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title": types.Schema(
                type=types.Type.STRING,
                description="The name/title of the event."
            ),
            "date": types.Schema(
                type=types.Type.STRING,
                description="The date in YYYY-MM-DD format."
            ),
            "start_time": types.Schema(
                type=types.Type.STRING,
                description="Start time in HH:MM format (24-hour)."
            ),
            "end_time": types.Schema(
                type=types.Type.STRING,
                description="End time in HH:MM format (24-hour)."
            ),
            "description": types.Schema(
                type=types.Type.STRING,
                description="Optional description or notes."
            )
        },
        required=["title", "date", "start_time", "end_time"]
    )
)

list_events_declaration = types.FunctionDeclaration(
    name="list_events",
    description=(
        "List calendar events. Optionally filter by date. "
        "Use this when the user asks about their schedule, upcoming meetings, "
        "or wants to see their calendar."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "date": types.Schema(
                type=types.Type.STRING,
                description="Optional date filter in YYYY-MM-DD format. Leave empty for all events."
            )
        },
        required=[]
    )
)

update_event_declaration = types.FunctionDeclaration(
    name="update_event",
    description=(
        "Update an existing calendar event. "
        "Use this when the user wants to change the time, date, or title of an event."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "event_id": types.Schema(
                type=types.Type.STRING,
                description="The ID of the event to update."
            ),
            "title": types.Schema(
                type=types.Type.STRING,
                description="New title (leave empty to keep current)."
            ),
            "date": types.Schema(
                type=types.Type.STRING,
                description="New date in YYYY-MM-DD format."
            ),
            "start_time": types.Schema(
                type=types.Type.STRING,
                description="New start time in HH:MM format."
            ),
            "end_time": types.Schema(
                type=types.Type.STRING,
                description="New end time in HH:MM format."
            ),
            "description": types.Schema(
                type=types.Type.STRING,
                description="New description."
            )
        },
        required=["event_id"]
    )
)

delete_event_declaration = types.FunctionDeclaration(
    name="delete_event",
    description=(
        "Delete a calendar event. "
        "Use this when the user wants to cancel or remove an event."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "event_id": types.Schema(
                type=types.Type.STRING,
                description="The ID of the event to delete."
            )
        },
        required=["event_id"]
    )
)

# ---------------------------------------------------------------------------
# Combine all tool declarations into a single Tool object.
# This is what we pass to Gemini so it knows all available tools.
# ---------------------------------------------------------------------------
all_tools = types.Tool(
    function_declarations=[
        execute_sql_declaration,
        list_tables_declaration,
        analyze_image_declaration,
        create_event_declaration,
        list_events_declaration,
        update_event_declaration,
        delete_event_declaration,
    ]
)


def get_tool_category(tool_name: str) -> str:
    """
    Get a human-readable category name for a tool.
    This is used in the UI to show which tool was selected.
    """
    sql_tools = ["execute_sql", "list_tables"]
    image_tools = ["analyze_image"]
    calendar_tools = ["create_event", "list_events", "update_event", "delete_event"]

    if tool_name in sql_tools:
        return "SQL Database Tool"
    elif tool_name in image_tools:
        return "Image Analysis Tool"
    elif tool_name in calendar_tools:
        return "Calendar Tool"
    else:
        return "Unknown Tool"


def process_user_request(user_message: str, image_path: str = None, table_info: str = "") -> dict:
    """
    Process a user's message using the Gemini AI Agent.

    This is the MAIN function of the agent. Here's what happens:
    1. We send the user's message to Gemini along with tool declarations
    2. Gemini analyzes the message and decides which tool to call
    3. We execute the tool via the MCP Client
    4. We send the tool result back to Gemini for a final response
    5. We return everything (logs, result, final response)

    Args:
        user_message: What the user typed (e.g., "Show all employees")
        image_path: Path to an uploaded image file (if any)
        table_info: Information about available database tables (helps the agent)

    Returns:
        Dictionary with:
        - tool_used: Which tool was selected (e.g., "SQL Database Tool")
        - tool_name: The function name (e.g., "execute_sql")
        - tool_input: What was sent to the tool
        - tool_output: What the tool returned
        - final_response: Gemini's natural language response
        - table_data: Structured table data (if SQL query returned rows)
    """

    # --- Build the system instruction ---
    # This tells Gemini about its role and what tools are available.
    # We include today's date so Gemini can handle "tomorrow", "next week", etc.
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    system_instruction = (
        "You are an AI assistant with access to three types of tools:\n"
        "1. SQL Database Tool - for querying data in SQLite tables\n"
        "2. Image Analysis Tool - for analyzing uploaded images\n"
        "3. Calendar Tool - for managing calendar events\n\n"
        f"Today's date is {today}. Tomorrow's date is {tomorrow}.\n"
        f"When the user says 'tomorrow', use the date {tomorrow}.\n\n"
        "For SQL queries:\n"
        "- Only generate SELECT queries (read-only)\n"
        "- If you need to know the available tables, use the list_tables tool first\n"
        f"- Available table information: {table_info}\n\n"
        "For calendar events:\n"
        "- Use 24-hour time format (HH:MM)\n"
        "- If the user doesn't specify an end time, assume 1 hour duration\n\n"
        "For image analysis:\n"
        "- An image must be uploaded for image analysis to work\n\n"
        "Always use the appropriate tool to answer the user's question.\n"
        "After getting the tool result, provide a clear, friendly response."
    )

    # --- Step 1: Send the user's message to Gemini with tool declarations ---
    # Create the Gemini client (checks for API key)
    client = get_gemini_client()
    if not client:
        return {
            "tool_used": "None",
            "tool_name": "none",
            "tool_input": user_message,
            "tool_output": "API key not configured",
            "final_response": "⚠️ Gemini API key not found. Please add your API key to the `.env` file.",
            "table_data": None
        }

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[all_tools],
                # temperature=0 makes the model more deterministic (less random)
                temperature=0,
            )
        )
    except Exception as e:
        return {
            "tool_used": "None",
            "tool_name": "none",
            "tool_input": user_message,
            "tool_output": str(e),
            "final_response": f"Error communicating with Gemini: {str(e)}",
            "table_data": None
        }

    # --- Step 2: Check if Gemini wants to call a tool ---
    # If Gemini decides a tool is needed, the response will contain a function_call
    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    # If there's no function call, Gemini answered directly (no tool needed)
    if not hasattr(part, 'function_call') or part.function_call is None:
        return {
            "tool_used": "None (Direct Response)",
            "tool_name": "none",
            "tool_input": user_message,
            "tool_output": "No tool was needed",
            "final_response": part.text if hasattr(part, 'text') else "I'm not sure how to help with that.",
            "table_data": None
        }

    # --- Step 3: Extract the tool name and arguments from Gemini's response ---
    function_call = part.function_call
    tool_name = function_call.name
    tool_args = dict(function_call.args) if function_call.args else {}

    tool_category = get_tool_category(tool_name)

    # --- Step 4: Execute the tool via MCP Client ---
    tool_result = {}
    table_data = None

    try:
        if tool_name in ["execute_sql", "list_tables"]:
            # Call the SQL MCP tool
            tool_result = run_sql_tool(tool_name, tool_args)

            # If the SQL query returned rows, prepare table data for display
            if tool_result.get("success") and "columns" in tool_result:
                table_data = {
                    "columns": tool_result["columns"],
                    "rows": tool_result["rows"]
                }

        elif tool_name == "analyze_image":
            # For image analysis, we need the image path
            if not image_path:
                tool_result = {
                    "success": False,
                    "error": "Please upload an image first."
                }
            else:
                instruction = tool_args.get("instruction", "Describe this image")
                tool_result = run_image_tool(image_path, instruction)

        elif tool_name in ["create_event", "list_events", "update_event", "delete_event"]:
            # Call the Calendar MCP tool
            tool_result = run_calendar_tool(tool_name, tool_args)

            # If listing events returned data, format as table
            if tool_result.get("success") and "events" in tool_result and tool_result["events"]:
                events = tool_result["events"]
                table_data = {
                    "columns": ["event_id", "title", "date", "start_time", "end_time", "description"],
                    "rows": [[e.get(c, "") for c in ["event_id", "title", "date", "start_time", "end_time", "description"]] for e in events]
                }

        else:
            tool_result = {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

    except Exception as e:
        tool_result = {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }

    # --- Step 5: Send the tool result back to Gemini for a final response ---
    # We give Gemini the original question + tool result so it can generate
    # a natural language answer.
    try:
        # Build the conversation history for the follow-up call
        # This tells Gemini: "You called this tool, here's what it returned"
        follow_up_contents = [
            # The user's original message
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            ),
            # Gemini's function call (what it decided to do)
            types.Content(
                role="model",
                parts=[types.Part.from_function_call(
                    name=tool_name,
                    args=tool_args
                )]
            ),
            # The tool's response (what the tool returned)
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result}
                )]
            )
        ]

        # Ask Gemini to generate a final natural language response
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=follow_up_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[all_tools],
                temperature=0,
            )
        )

        final_text = final_response.text

    except Exception as e:
        # If the follow-up fails, create a response from the tool result
        if tool_result.get("success"):
            final_text = f"Tool executed successfully. Result: {json.dumps(tool_result, indent=2)}"
        else:
            final_text = f"Tool returned an error: {tool_result.get('error', 'Unknown error')}"

    # --- Step 6: Return everything to the UI ---
    return {
        "tool_used": tool_category,
        "tool_name": tool_name,
        "tool_input": tool_args,
        "tool_output": tool_result,
        "final_response": final_text,
        "table_data": table_data
    }
