"""
Streamlit UI — Main Application
=================================
This is the entry point of the AI Agent application.
Run it with: streamlit run app.py

It provides:
- A chat interface for talking to the AI Agent
- CSV file upload for database queries
- Image upload for image analysis
- Calendar event management
- Result display with download options
- Tool selection logs for learning
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import json
import io
from datetime import datetime

# Import our AI Agent
from agent import process_user_request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Page Configuration
# This must be the first Streamlit command in the script.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Agent with MCP Tools",
    page_icon="🤖",
    layout="wide"
)

# Show a warning if the API key is not set
if not os.getenv("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY not found. Please add your API key to the `.env` file.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Path to the SQLite database for uploaded CSV data
DB_PATH = os.path.join("data", "database.db")

# Folder where uploaded images are saved
UPLOADS_DIR = "uploads"

# Create the uploads folder if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def import_csv_to_sqlite(uploaded_file, table_name: str):
    """
    Import a CSV file into a SQLite table.

    This function:
    1. Reads the CSV file using pandas
    2. Creates a SQLite table with the same name as the file
    3. Inserts all rows from the CSV into the table

    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        table_name: Name for the SQLite table (derived from filename)
    """
    try:
        # Read the CSV into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Connect to SQLite and save the DataFrame as a table
        # if_exists="replace" means it will overwrite if the table already exists
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()

        return True, f"✅ Imported **{table_name}** ({len(df)} rows, {len(df.columns)} columns)"

    except Exception as e:
        return False, f"❌ Error importing {table_name}: {str(e)}"


def import_excel_to_sqlite(uploaded_file, table_name: str):
    """
    Import an Excel file into a SQLite table.
    Works the same as CSV import but reads .xlsx files.
    """
    try:
        df = pd.read_excel(uploaded_file)
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        return True, f"✅ Imported **{table_name}** ({len(df)} rows, {len(df.columns)} columns)"
    except Exception as e:
        return False, f"❌ Error importing {table_name}: {str(e)}"


def get_table_info() -> str:
    """
    Get information about all tables in the database.
    This is passed to the AI agent so it knows what data is available.

    Returns:
        A string describing all tables and their columns.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            conn.close()
            return "No tables available. Please upload CSV files."

        info_parts = []
        for table in tables:
            # Get column info for each table
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            info_parts.append(f"Table '{table}': columns = {col_names}")

        conn.close()
        return "; ".join(info_parts)

    except Exception:
        return "No tables available."


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to Excel bytes for download."""
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    return output.getvalue()


# ---------------------------------------------------------------------------
# Initialize Session State
# Streamlit reruns the entire script on each interaction.
# Session state lets us keep data between reruns.
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat message history

if "uploaded_image_path" not in st.session_state:
    st.session_state.uploaded_image_path = None  # Path to current uploaded image


# ---------------------------------------------------------------------------
# App Title and Header
# ---------------------------------------------------------------------------
st.title("🤖 AI Agent with MCP Tools")
st.caption("Ask questions about your data, analyze images, or manage your calendar — powered by Gemini + MCP")

# ---------------------------------------------------------------------------
# Sidebar — File Uploads and Info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📁 Upload Data")
    st.caption("Upload CSV or Excel files to create database tables for SQL queries.")

    # CSV/Excel file uploader
    data_files = st.file_uploader(
        "Upload CSV / Excel files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="data_uploader"
    )

    # Process uploaded data files
    if data_files:
        for uploaded_file in data_files:
            # Get the table name from the filename (remove extension)
            # Example: "employees.csv" → "employees"
            file_name = uploaded_file.name
            table_name = os.path.splitext(file_name)[0].lower().replace(" ", "_")

            if file_name.endswith(".csv"):
                success, message = import_csv_to_sqlite(uploaded_file, table_name)
            else:
                success, message = import_excel_to_sqlite(uploaded_file, table_name)

            if success:
                st.success(message)
            else:
                st.error(message)

    # Show currently available tables
    table_info = get_table_info()
    if "No tables" not in table_info:
        st.divider()
        st.subheader("📊 Available Tables")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            for t in tables:
                st.code(t, language=None)
        except Exception:
            pass

    st.divider()

    # Image file uploader
    st.header("🖼️ Upload Image")
    st.caption("Upload an image file for AI analysis.")

    image_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "bmp", "gif", "webp"],
        key="image_uploader"
    )

    # Save the uploaded image to disk
    if image_file:
        image_save_path = os.path.join(UPLOADS_DIR, image_file.name)
        with open(image_save_path, "wb") as f:
            f.write(image_file.getbuffer())
        st.session_state.uploaded_image_path = image_save_path
        st.success(f"✅ Image uploaded: **{image_file.name}**")
        st.image(image_file, caption=image_file.name, use_container_width=True)

    st.divider()

    # Quick help
    st.header("💡 Try These")
    st.markdown("""
    **SQL queries:**
    - "Show all employees"
    - "Average salary by department"
    - "Total sales by city"
    - "Top 5 employees by salary"

    **Image analysis:**
    - "Describe this image"
    - "What objects are in the image?"

    **Calendar:**
    - "Create a meeting tomorrow at 3 PM"
    - "What events do I have?"
    """)


# ---------------------------------------------------------------------------
# Main Chat Area
# ---------------------------------------------------------------------------

# Display previous messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # If the message has table data, show it again
        if "table_data" in message and message["table_data"]:
            df = pd.DataFrame(
                message["table_data"]["rows"],
                columns=message["table_data"]["columns"]
            )
            st.dataframe(df, use_container_width=True)

        # Show logs if they exist
        if "logs" in message and message["logs"]:
            with st.expander("🔍 Agent Logs"):
                st.code(message["logs"], language=None)


# ---------------------------------------------------------------------------
# Chat Input — Where the user types their question
# ---------------------------------------------------------------------------
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Add the user's message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display the user's message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show a spinner while the agent processes the request
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):

            # Get table info for the SQL agent to use
            table_info = get_table_info()

            # Get the image path (if an image was uploaded)
            image_path = st.session_state.uploaded_image_path

            # ------------------------------------
            # Call the AI Agent!
            # This is where the magic happens.
            # ------------------------------------
            result = process_user_request(
                user_message=user_input,
                image_path=image_path,
                table_info=table_info
            )

        # --- Display the final response ---
        st.markdown(result["final_response"])

        # --- Display table data if available ---
        if result.get("table_data"):
            df = pd.DataFrame(
                result["table_data"]["rows"],
                columns=result["table_data"]["columns"]
            )
            st.dataframe(df, use_container_width=True)

            # Download buttons for the table data
            col1, col2 = st.columns(2)
            with col1:
                csv_data = convert_df_to_csv(df)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="query_result.csv",
                    mime="text/csv"
                )
            with col2:
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="query_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # --- Display Agent Logs ---
        # These logs show what the agent did behind the scenes.
        # Very helpful for learning and debugging!
        log_text = (
            f"User Request:\n{user_input}\n\n"
            f"Agent Decision:\n{result['tool_used']}\n\n"
            f"Tool Called:\n{result['tool_name']}\n\n"
            f"Tool Input:\n{json.dumps(result['tool_input'], indent=2) if isinstance(result['tool_input'], dict) else result['tool_input']}\n\n"
            f"Tool Output:\n{json.dumps(result['tool_output'], indent=2) if isinstance(result['tool_output'], dict) else result['tool_output']}\n\n"
            f"Final Response:\n{result['final_response']}"
        )

        with st.expander("🔍 Agent Logs — See what the agent did"):
            st.code(log_text, language=None)

        # Save the assistant's response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["final_response"],
            "table_data": result.get("table_data"),
            "logs": log_text
        })
