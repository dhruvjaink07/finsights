import google.generativeai as genai
import os
import hashlib
import json
import asyncio

CACHE_FILE = "gemini_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        GEMINI_CACHE = json.load(f)
else:
    GEMINI_CACHE = {}

def cache_gemini_insight(prompt, response=None):
    key = hashlib.sha256(prompt.encode()).hexdigest()
    if response is not None:
        GEMINI_CACHE[key] = response
        with open(CACHE_FILE, "w") as f:
            json.dump(GEMINI_CACHE, f)
    return GEMINI_CACHE.get(key)

def get_gemini_insight(prompt: str) -> str:
    cached = cache_gemini_insight(prompt)
    if cached:
        print("[Gemini] Loaded from cache.")
        return cached
    print("[Gemini] Calling Gemini API...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    result = response.text.strip() if hasattr(response, "text") else str(response)
    cache_gemini_insight(prompt, result)
    return result

async def get_gemini_insight_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_gemini_insight, prompt)