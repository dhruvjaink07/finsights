import asyncio
from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from utils.news_fetcher import NewsFetcherAdapter

def print_sentiment_results(sentiment_data):
    for company, articles in sentiment_data.items():
        print(f"\n=== {company} ===")
        if not articles:
            print("  No news articles found.")
            continue
        for art in articles:
            print(f"Headline: {art['headline']}")
            print(f"  Sentiment: {art['sentiment']} (score: {art['score']})")
            print("-" * 40)

async def main():
    supervisor = SupervisorAgent()
    supervisor.register_agent(MarketDataAgent())
    supervisor.register_agent(SentimentAgent(NewsFetcherAdapter()))
    supervisor.register_agent(InsightAgent(None, None))

    # Step 1: Run MarketDataAgent to get stock data
    market_task = {
        "agent_name": "MarketDataAgent",
        "task_type": "fetch_top_stocks",
        "parameters": {"count": 3},
        "priority": 1,
        "retries": 2
    }
    market_result = await supervisor.agents["MarketDataAgent"].execute(market_task)
    print("MarketDataAgent result:", market_result.data)

    # Step 2: Extract symbols from MarketDataAgent result
    if market_result.success and market_result.data:
        first_row = market_result.data[0]
        symbols = [k[1] for k in first_row.keys() if k[0] == 'Close']
    else:
        symbols = []

    print("Symbols for SentimentAgent:", symbols)

    # Step 3: Run SentimentAgent with extracted symbols
    sentiment_task = {
        "agent_name": "SentimentAgent",
        "task_type": "analyze_news",
        "parameters": {"symbols": symbols},
        "priority": 2
    }
    sentiment_result = await supervisor.agents["SentimentAgent"].execute(sentiment_task)
    print("SentimentAgent result:", sentiment_result.data)

    print_sentiment_results(sentiment_result.data)

    # Step 4: Run InsightAgent (optional, using dummy data)
    insight_task = {
        "agent_name": "InsightAgent",
        "task_type": "generate_summary",
        "parameters": {
            "market_data": market_result.data,
            "sentiment": sentiment_result.data
        },
        "priority": 3
    }
    insight_result = await supervisor.agents["InsightAgent"].execute(insight_task)
    print("InsightAgent result:", insight_result.data)

if __name__ == "__main__":
    asyncio.run(main())