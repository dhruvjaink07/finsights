import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from utils.gemini_helpers import get_gemini_insight, CACHE_FILE

def test_gemini_caching():
    prompt = "Test prompt for Gemini caching. Summarize: Apple stock is up 2% today with positive sentiment."
    
    # Remove cache file if exists for a clean test
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    
    # First call: should NOT be cached (should take longer)
    start = time.time()
    response1 = get_gemini_insight(prompt)
    duration1 = time.time() - start
    print(f"First call duration: {duration1:.2f}s, response: {response1[:60]}...")
    
    # Second call: should be cached (should be fast)
    start = time.time()
    response2 = get_gemini_insight(prompt)
    duration2 = time.time() - start
    print(f"Second call duration: {duration2:.2f}s, response: {response2[:60]}...")
    
    assert response1 == response2, "Cached response does not match original!"
    assert duration2 < duration1, "Second call should be faster due to caching!"
    print("✅ Gemini caching works as expected.")

if __name__ == "__main__":
    test_gemini_caching()