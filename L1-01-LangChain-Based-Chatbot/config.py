"""
config.py — Application Configuration

Loads environment variables from .env file and provides
configuration values to the rest of the application.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# Read configuration values from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash")
# TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))


def validate_config():
    """Check that required configuration values are present."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY is missing. "
            "Please set it in your .env file."
        )
