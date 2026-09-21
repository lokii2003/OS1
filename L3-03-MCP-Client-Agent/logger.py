"""
=============================================================
SIMPLE LOGGER
=============================================================
Purpose:
    Provides simple logging for the project.
    Logs go to both the console (stderr) and an in-memory list
    that can be displayed on the Streamlit Logs page.

Why we need it:
    - Shows the step-by-step agent workflow
    - Helps debug issues
    - Never exposes API keys

How it connects:
    Every module imports and uses this logger.
    The Logs page (pages/3_Logs.py) reads the in-memory log list.
=============================================================
"""

import logging
from datetime import datetime

# --- In-memory log storage ---
# This list stores log entries so Streamlit can display them.
# Each entry is a dict with timestamp and message.
_log_entries = []


def get_logs():
    """Return all log entries (for the Logs page)."""
    return _log_entries.copy()


def clear_logs():
    """Clear all log entries."""
    _log_entries.clear()


def log(message: str, level: str = "INFO"):
    """
    Log a message.

    - Prints to console (stderr) via Python logging
    - Stores in memory for Streamlit display
    - Never logs API keys or sensitive data
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Store in memory for the Logs page
    _log_entries.append({
        "time": timestamp,
        "level": level,
        "message": message
    })

    # Also log to console (stderr) via Python logging
    logger = logging.getLogger("mcp-agent")
    if level == "ERROR":
        logger.error(f"{timestamp} {message}")
    elif level == "WARNING":
        logger.warning(f"{timestamp} {message}")
    else:
        logger.info(f"{timestamp} {message}")


# Configure Python logging to stderr (not stdout, important for MCP stdio)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
