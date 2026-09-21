"""
Image Analysis MCP Tool Server
================================
This file creates an MCP server with one tool: analyze_image.
It uses Gemini's vision/multimodal capability to analyze images.
The AI agent sends an image path + instruction here, and this tool
calls Gemini Vision to analyze the image.
"""

import json
import os
from fastmcp import FastMCP
from PIL import Image
from google import genai
from dotenv import load_dotenv

# Load environment variables (for the API key)
load_dotenv()

# ---------------------------------------------------------------------------
# Create the MCP server for image analysis.
# ---------------------------------------------------------------------------
image_server = FastMCP("Image Analysis Tool")

# ---------------------------------------------------------------------------
# Set up the Gemini client for vision/multimodal analysis.
# We use a separate Gemini client here because this tool needs
# to send images directly to Gemini's vision model.
# ---------------------------------------------------------------------------


def get_gemini_client():
    """
    Create and return a Gemini API client.
    We create it on-demand (not at import time) so that:
    1. The API key can be set after import
    2. We get a fresh client each time (avoids stale connections)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# The main MCP tool: analyze_image
# This is what the AI agent calls when the user wants to analyze an image.
# ---------------------------------------------------------------------------
@image_server.tool()
def analyze_image(image_path: str, instruction: str) -> str:
    """
    Analyze an uploaded image using Gemini's vision capability.
    Use this tool when the user asks to describe an image, identify objects,
    read text in an image, or answer any question about an uploaded image.

    Args:
        image_path: The file path to the image on disk.
        instruction: What the user wants to know about the image
                    (e.g., "Describe this image", "What objects are in this image?")

    Returns:
        JSON string with the analysis result on success.
        JSON string with error message on failure.
    """
    try:
        # Step 1: Check if the image file exists
        if not image_path or not os.path.exists(image_path):
            return json.dumps({
                "success": False,
                "error": "Please upload an image first. No image file found."
            })

        # Step 2: Create the Gemini client
        client = get_gemini_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."
            })

        # Step 3: Open the image using PIL (Python Imaging Library)
        # PIL can handle many image formats: JPEG, PNG, BMP, GIF, etc.
        image = Image.open(image_path)

        # Step 4: Send the image + instruction to Gemini Vision
        # Gemini can understand both text and images together (multimodal)
        # We pass a list: [image, text_instruction]
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[image, instruction]
        )

        # Step 5: Extract the text response from Gemini
        analysis_text = response.text

        # Step 6: Return the analysis result
        return json.dumps({
            "success": True,
            "analysis": analysis_text
        })

    except Exception as e:
        # Handle any errors gracefully
        return json.dumps({
            "success": False,
            "error": f"Image analysis failed: {str(e)}"
        })
