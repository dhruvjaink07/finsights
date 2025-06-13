import asyncio
from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from utils.news_fetcher import NewsFetcherAdapter

# Dummy classes for testing
class DummySentimentAnalyzer:
    def analyze(self, content):
        return "positive"

async def main():
    # Initialize agents
    supervisor = SupervisorAgent()
    supervisor.register_agent(MarketDataAgent())
    supervisor.register_agent(
        SentimentAgent(NewsFetcherAdapter(), DummySentimentAnalyzer())
    )
    supervisor.register_agent(InsightAgent(None, None))  # Pass dummy args if needed

    # Define workflow
    workflow = [
        {
            "agent_name": "MarketDataAgent",
            "task_type": "fetch_top_stocks",
            "parameters": {"count": 10},
            "priority": 1,
            "retries": 2
        },
        {
            "agent_name": "SentimentAgent",
            "task_type": "analyze_news",
            "parameters": {"symbols": "{{MarketDataAgent.result}}"},
            "priority": 2
        },
        {
            "agent_name": "InsightAgent",
            "task_type": "generate_summary",
            "parameters": {
                "market_data": "{{MarketDataAgent.result}}",
                "sentiment": "{{SentimentAgent.result}}"
            },
            "priority": 3
        }
    ]

    # Execute workflow
    results = await supervisor.execute_workflow(workflow)
    print("Workflow results:", results)

if __name__ == "__main__":
    asyncio.run(main())