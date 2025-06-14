import google.generativeai as genai
import os

def get_gemini_insight(prompt: str) -> str:
    """
    Get an insight from Gemini based on the provided prompt.
    
    Args:
        prompt (str): The prompt to send to Gemini.
        
    Returns:
        str: The response from Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, "text") else str(response)