"""
AI Service Module

This file contains the logic for classifying civic issue reports.
It is designed to be easily updated to call a real, external AI model.
"""
import os
import httpx
from typing import List

# --- Configuration for the Real AI Model ---
# Your teammate will provide this URL. It's the address of their running AI service.
# We use an environment variable for security and flexibility.
REAL_AI_API_URL = os.getenv("AI_API_URL", "http://127.0.0.1:8001/api/classify") # Example URL

# A timeout for the API call to prevent our app from waiting indefinitely.
AI_API_TIMEOUT = 10.0 # 10 seconds

async def classify_report_with_real_ai(description: str, image_urls: List[str]) -> str:
    """
    Calls a real, external AI model to classify a report.
    
    This function sends the report's description and image URLs to the AI service
    and returns its classification. It includes error handling and a fallback.

    Args:
        description: The text description of the civic issue.
        image_urls: A list of public URLs for the report's images.

    Returns:
        A string representing the classified category from the AI model,
        or a fallback category if the AI service fails.
    """
    try:
        # We use an async HTTP client to avoid blocking our main application.
        async with httpx.AsyncClient() as client:
            # The data payload we will send to the AI model.
            # Your teammate should define the exact structure they expect.
            payload = {
                "description": description,
                "image_urls": image_urls
            }
            
            print(f"--- Calling Real AI Service at {REAL_AI_API_URL} ---")
            
            # Make the POST request to the AI service.
            response = await client.post(REAL_AI_API_URL, json=payload, timeout=AI_API_TIMEOUT)
            
            # Raise an exception if the AI service returns an error (like 500).
            response.raise_for_status()
            
            # Assuming the AI returns JSON like: {"category": "Pothole"}
            ai_category = response.json().get("category")
            
            if not ai_category:
                print("--- AI WARNING: AI service did not return a category. ---")
                return "General Inquiry"
                
            print(f"--- Real AI Responded with Category: {ai_category} ---")
            return ai_category

    except httpx.RequestError as e:
        # This catches network errors (e.g., the AI service is down).
        print(f"--- AI ERROR: Could not connect to AI service: {e} ---")
        return "Classification Pending"
    except Exception as e:
        # This catches all other errors (e.g., invalid response from AI).
        print(f"--- AI ERROR: An unexpected error occurred: {e} ---")
        return "Classification Pending"

def classify_report_simulated(description: str) -> str:
    """
    Simulates an AI model classifying a report based on keywords.
    """
    description_lower = description.lower()
    if any(keyword in description_lower for keyword in ["pothole", "hole", "crack", "road damage"]):
        return "Pothole"
    if any(keyword in description_lower for keyword in ["light", "lamp", "bulb", "streetlight"]):
        return "Streetlight Outage"
    if any(keyword in description_lower for keyword in ["garbage", "trash", "waste", "bin"]):
        return "Waste Management"
    if any(keyword in description_lower for keyword in ["tree", "branch", "overgrown"]):
        return "Fallen Tree / Landscaping"
    
    return "General Inquiry"

