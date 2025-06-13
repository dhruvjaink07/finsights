import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from agents.sentiment_agent import SentimentAgent
from utils.news_fetcher import NewsFetcherAdapter

async def test_sentiment_agent():
    agent = SentimentAgent(NewsFetcherAdapter())
    # Example task for testing
    task = {
        "task_type": "analyze_news",
        "parameters": {"symbols": "RELIANCE"}
    }
    result = await agent.execute(task)
    print("SentimentAgent result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_sentiment_agent())