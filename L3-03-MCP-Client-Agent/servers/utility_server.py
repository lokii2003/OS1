"""
=============================================================
UTILITY MCP SERVER
=============================================================
Purpose:
    This is an MCP server that provides two tools:
    1. get_weather  — Returns DEMO weather data for a city
    2. get_current_time — Returns the REAL current time for a timezone

Why we need it:
    MCP servers expose "tools" over a standard protocol.
    The AI agent discovers and calls these tools dynamically.

How it connects:
    MCP Client (mcp_client.py) connects to this server via stdio.
    The client calls session.list_tools() to discover these tools.
    The client calls session.call_tool() to execute them.

Run:
    python servers/utility_server.py
=============================================================
"""

from datetime import datetime
from zoneinfo import ZoneInfo          # Python 3.9+ timezone support
from mcp.server.mcpserver import MCPServer  # MCP SDK v2 server class

# --- Create the MCP server instance ---
mcp = MCPServer("UtilityServer")


# -----------------------------------------------
# TOOL 1: get_weather
# -----------------------------------------------
# This is a DEMO tool. It returns fake weather data.
# In a real project, you would call a weather API here.
# -----------------------------------------------
@mcp.tool()
def get_weather(city: str) -> str:
    """Returns demo weather information for a given city. This is mock data, not live weather."""

    # Simple demo data — different cities get different weather
    demo_weather = {
        "pune":      {"temp": "28°C", "condition": "Partly Cloudy", "humidity": "65%"},
        "mumbai":    {"temp": "32°C", "condition": "Humid & Sunny", "humidity": "80%"},
        "delhi":     {"temp": "35°C", "condition": "Hazy",          "humidity": "45%"},
        "bangalore": {"temp": "24°C", "condition": "Pleasant",      "humidity": "70%"},
        "london":    {"temp": "15°C", "condition": "Overcast",      "humidity": "75%"},
        "new york":  {"temp": "22°C", "condition": "Clear Sky",     "humidity": "55%"},
        "tokyo":     {"temp": "26°C", "condition": "Warm & Humid",  "humidity": "72%"},
    }

    # Look up the city (case-insensitive)
    city_lower = city.lower().strip()
    weather = demo_weather.get(city_lower, {
        "temp": "25°C", "condition": "Sunny", "humidity": "60%"
    })

    return (
        f"⚠️ DEMO WEATHER DATA (not live)\n"
        f"City: {city}\n"
        f"Temperature: {weather['temp']}\n"
        f"Condition: {weather['condition']}\n"
        f"Humidity: {weather['humidity']}"
    )


# -----------------------------------------------
# TOOL 2: get_current_time
# -----------------------------------------------
# This returns the REAL current time.
# Uses Python's built-in zoneinfo module.
# -----------------------------------------------
@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """Returns the current time for a given timezone (e.g., 'Asia/Kolkata', 'US/Eastern', 'UTC')."""
    try:
        # Get current time in the requested timezone
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)

        return (
            f"Timezone: {timezone}\n"
            f"Current Time: {now.strftime('%I:%M:%S %p')}\n"
            f"Date: {now.strftime('%A, %B %d, %Y')}"
        )
    except KeyError:
        # If the timezone name is invalid
        return f"Error: Unknown timezone '{timezone}'. Try 'Asia/Kolkata', 'US/Eastern', or 'UTC'."


# --- Run the server ---
# mcp.run() starts the server using stdio transport (default).
# The MCP client will spawn this as a subprocess and communicate via stdin/stdout.
if __name__ == "__main__":
    mcp.run()
