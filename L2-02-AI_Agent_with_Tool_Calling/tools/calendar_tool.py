"""
Calendar MCP Tool Server
=========================
This file creates an MCP server with calendar management tools.
It uses a local SQLite database to store calendar events.
No external calendar API (like Google Calendar) is needed.

Tools provided:
- create_event: Create a new calendar event
- list_events: List events for a date or date range
- update_event: Update an existing event
- delete_event: Delete an event
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Create the MCP server for calendar operations.
# ---------------------------------------------------------------------------
calendar_server = FastMCP("Calendar Tool")

# Path to our calendar SQLite database (separate from the main data DB)
CALENDAR_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "calendar.db")


def init_calendar_db():
    """
    Initialize the calendar database by creating the events table if it
    doesn't exist yet. This runs automatically when the tool is first used.

    Table structure:
    - event_id: Unique identifier for each event
    - title: Name/description of the event
    - date: The date of the event (YYYY-MM-DD format)
    - start_time: Start time (HH:MM format)
    - end_time: End time (HH:MM format)
    - description: Optional longer description
    - created_at: When the event was created
    """
    conn = sqlite3.connect(CALENDAR_DB_PATH)
    cursor = conn.cursor()

    # Create the events table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Make sure the calendar database and table exist
init_calendar_db()


# ---------------------------------------------------------------------------
# Tool 1: create_event
# Creates a new calendar event and saves it to the database.
# ---------------------------------------------------------------------------
@calendar_server.tool()
def create_event(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    description: str = ""
) -> str:
    """
    Create a new calendar event.
    Use this when the user wants to schedule a meeting, appointment, or any event.

    Args:
        title: The name of the event (e.g., "Meeting with Rahul")
        date: The date in YYYY-MM-DD format (e.g., "2026-09-18")
        start_time: Start time in HH:MM format (e.g., "15:00")
        end_time: End time in HH:MM format (e.g., "16:00")
        description: Optional description or notes for the event

    Returns:
        JSON string with event_id and success message.
    """
    try:
        # Validate the date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "success": False,
                "error": f"Invalid date format: '{date}'. Please use YYYY-MM-DD format."
            })

        # Validate the time format
        for time_str, label in [(start_time, "start_time"), (end_time, "end_time")]:
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid {label} format: '{time_str}'. Please use HH:MM format."
                })

        # Generate a unique event ID
        event_id = str(uuid.uuid4())[:8]  # Use first 8 chars for simplicity

        # Insert the event into the database
        conn = sqlite3.connect(CALENDAR_DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO events (event_id, title, date, start_time, end_time, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (event_id, title, date, start_time, end_time, description)
        )

        conn.commit()
        conn.close()

        return json.dumps({
            "success": True,
            "event_id": event_id,
            "message": f"Event '{title}' created successfully on {date} from {start_time} to {end_time}."
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to create event: {str(e)}"
        })


# ---------------------------------------------------------------------------
# Tool 2: list_events
# Lists calendar events, optionally filtered by date.
# ---------------------------------------------------------------------------
@calendar_server.tool()
def list_events(date: str = "") -> str:
    """
    List calendar events. If a date is provided, shows events for that date.
    If no date is provided, shows all upcoming events.
    Use this when the user asks about their schedule, meetings, or events.

    Args:
        date: Optional date filter in YYYY-MM-DD format.
              Leave empty to list all events.

    Returns:
        JSON string with a list of events.
    """
    try:
        conn = sqlite3.connect(CALENDAR_DB_PATH)
        cursor = conn.cursor()

        if date:
            # Filter events by the specified date
            cursor.execute(
                "SELECT event_id, title, date, start_time, end_time, description "
                "FROM events WHERE date = ? ORDER BY start_time",
                (date,)
            )
        else:
            # Show all events, sorted by date and time
            cursor.execute(
                "SELECT event_id, title, date, start_time, end_time, description "
                "FROM events ORDER BY date, start_time"
            )

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            message = f"No events found for {date}." if date else "No events found."
            return json.dumps({
                "success": True,
                "events": [],
                "message": message
            })

        # Convert rows to a list of dictionaries for readability
        events = []
        for row in rows:
            events.append({
                "event_id": row[0],
                "title": row[1],
                "date": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "description": row[5]
            })

        return json.dumps({
            "success": True,
            "events": events,
            "count": len(events)
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to list events: {str(e)}"
        })


# ---------------------------------------------------------------------------
# Tool 3: update_event
# Updates an existing calendar event.
# ---------------------------------------------------------------------------
@calendar_server.tool()
def update_event(
    event_id: str,
    title: str = "",
    date: str = "",
    start_time: str = "",
    end_time: str = "",
    description: str = ""
) -> str:
    """
    Update an existing calendar event.
    Use this when the user wants to change the time, date, or title of an event.

    Args:
        event_id: The ID of the event to update.
        title: New title (leave empty to keep current).
        date: New date in YYYY-MM-DD format (leave empty to keep current).
        start_time: New start time in HH:MM format (leave empty to keep current).
        end_time: New end time in HH:MM format (leave empty to keep current).
        description: New description (leave empty to keep current).

    Returns:
        JSON string with success/failure message.
    """
    try:
        conn = sqlite3.connect(CALENDAR_DB_PATH)
        cursor = conn.cursor()

        # First check if the event exists
        cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        event = cursor.fetchone()

        if not event:
            conn.close()
            return json.dumps({
                "success": False,
                "error": f"The requested event with ID '{event_id}' was not found."
            })

        # Build the update query dynamically based on which fields were provided
        updates = []
        values = []

        if title:
            updates.append("title = ?")
            values.append(title)
        if date:
            updates.append("date = ?")
            values.append(date)
        if start_time:
            updates.append("start_time = ?")
            values.append(start_time)
        if end_time:
            updates.append("end_time = ?")
            values.append(end_time)
        if description:
            updates.append("description = ?")
            values.append(description)

        if not updates:
            conn.close()
            return json.dumps({
                "success": False,
                "error": "No fields to update. Please provide at least one field to change."
            })

        # Add the event_id to the values for the WHERE clause
        values.append(event_id)

        # Execute the update
        query = f"UPDATE events SET {', '.join(updates)} WHERE event_id = ?"
        cursor.execute(query, values)

        conn.commit()
        conn.close()

        return json.dumps({
            "success": True,
            "message": f"Event '{event_id}' updated successfully."
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to update event: {str(e)}"
        })


# ---------------------------------------------------------------------------
# Tool 4: delete_event
# Deletes a calendar event from the database.
# ---------------------------------------------------------------------------
@calendar_server.tool()
def delete_event(event_id: str) -> str:
    """
    Delete a calendar event.
    Use this when the user wants to cancel or remove an event.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        JSON string with success/failure message.
    """
    try:
        conn = sqlite3.connect(CALENDAR_DB_PATH)
        cursor = conn.cursor()

        # Check if the event exists before deleting
        cursor.execute("SELECT title FROM events WHERE event_id = ?", (event_id,))
        event = cursor.fetchone()

        if not event:
            conn.close()
            return json.dumps({
                "success": False,
                "error": f"The requested event with ID '{event_id}' was not found."
            })

        # Delete the event
        cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))

        conn.commit()
        conn.close()

        return json.dumps({
            "success": True,
            "message": f"Event '{event[0]}' (ID: {event_id}) deleted successfully."
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to delete event: {str(e)}"
        })
