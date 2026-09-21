"""
SQL MCP Tool Server
===================
This file creates an MCP server with one tool: execute_sql.
It connects to a local SQLite database and runs read-only SQL queries.
The AI agent sends SQL here, and this tool executes it safely.
"""

import sqlite3
import json
import os
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Create the MCP server for SQL operations.
# FastMCP automatically handles the MCP protocol (JSON-RPC, tool schemas, etc.)
# ---------------------------------------------------------------------------
sql_server = FastMCP("SQL Database Tool")

# Path to our SQLite database file
# os.path.dirname(__file__) gets the folder where this script lives (tools/)
# We go one level up (..) to reach the project root, then into data/
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "database.db")

# ---------------------------------------------------------------------------
# List of dangerous SQL commands that we block for safety.
# We only allow SELECT queries (read-only).
# ---------------------------------------------------------------------------
BLOCKED_COMMANDS = ["DROP", "DELETE", "UPDATE", "ALTER", "TRUNCATE", "INSERT", "CREATE"]


def is_safe_query(query: str) -> bool:
    """
    Check if a SQL query is safe to execute.
    We only allow read-only queries (SELECT).
    Returns True if the query is safe, False if it contains dangerous commands.
    """
    # Convert to uppercase for checking
    query_upper = query.strip().upper()

    # Check if the query starts with or contains any blocked command
    for command in BLOCKED_COMMANDS:
        # Check if the blocked command appears as a standalone word
        if query_upper.startswith(command) or f" {command} " in f" {query_upper} ":
            return False

    return True


def get_table_names() -> list:
    """
    Get a list of all table names in the database.
    This helps the AI agent know which tables are available.
    Returns a list of table name strings.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # SQLite stores table info in a special table called sqlite_master
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Get all table names as a flat list
        tables = [row[0] for row in cursor.fetchall()]

        # Always close the connection when done
        conn.close()
        return tables

    except Exception as e:
        return []


def get_table_schema(table_name: str) -> list:
    """
    Get the column names and types for a specific table.
    This helps the AI agent understand the table structure.
    Returns a list of dicts with column info.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # PRAGMA table_info returns column details for a table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        conn.close()

        # Each row from PRAGMA: (id, name, type, notnull, default, pk)
        return [{"name": col[1], "type": col[2]} for col in columns]

    except Exception as e:
        return []


# ---------------------------------------------------------------------------
# The main MCP tool: execute_sql
# This is what the AI agent calls when it needs to query the database.
# The @sql_server.tool() decorator registers this function as an MCP tool.
# ---------------------------------------------------------------------------
@sql_server.tool()
def execute_sql(query: str) -> str:
    """
    Execute a read-only SQL query against the SQLite database.
    Use this tool when the user asks questions about data stored in database tables.
    This includes questions about employees, sales, departments, counts, averages,
    totals, joins, filtering, sorting, or any data analysis.

    Args:
        query: The SQL query to execute. Must be a SELECT query (read-only).

    Returns:
        JSON string with columns, rows, and row_count on success.
        JSON string with error message on failure.
    """
    try:
        # Step 1: Check if the query is safe (read-only)
        if not is_safe_query(query):
            return json.dumps({
                "success": False,
                "error": "Only read-only SELECT queries are allowed. "
                         "DROP, DELETE, UPDATE, ALTER, INSERT, CREATE are blocked."
            })

        # Step 2: Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Step 3: Execute the SQL query sent by the AI agent
        cursor.execute(query)

        # Step 4: Get column names from the cursor description
        # cursor.description contains metadata about each column
        columns = [description[0] for description in cursor.description]

        # Step 5: Get all rows returned by the database
        rows = cursor.fetchall()

        # Step 6: Close the database connection
        conn.close()

        # Step 7: Return the result as a JSON string
        return json.dumps({
            "success": True,
            "columns": columns,
            "rows": [list(row) for row in rows],  # Convert tuples to lists
            "row_count": len(rows)
        })

    except Exception as e:
        # If anything goes wrong, return a friendly error message
        error_message = str(e)

        # Check for common errors and give helpful messages
        if "no such table" in error_message:
            return json.dumps({
                "success": False,
                "error": f"Table not found. {error_message}. "
                         f"Available tables: {get_table_names()}"
            })

        return json.dumps({
            "success": False,
            "error": f"SQL execution failed: {error_message}"
        })


@sql_server.tool()
def list_tables() -> str:
    """
    List all tables available in the database along with their column information.
    Use this tool when the user wants to know what tables or data are available,
    or when you need to understand the database structure before writing a query.

    Returns:
        JSON string with table names and their schemas.
    """
    try:
        tables = get_table_names()

        if not tables:
            return json.dumps({
                "success": True,
                "tables": [],
                "message": "No tables found. Please upload CSV files first."
            })

        # Get schema for each table
        table_info = {}
        for table in tables:
            table_info[table] = get_table_schema(table)

        return json.dumps({
            "success": True,
            "tables": table_info
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to list tables: {str(e)}"
        })
