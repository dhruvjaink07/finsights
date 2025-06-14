from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from agents.visualization_agent import VisualizationAgent
from utils.news_fetcher import NewsFetcherAdapter
import asyncio
import copy
import pandas as pd

async def run_workflow(supervisor, workflow):
    results = {}
    for step in workflow:
        agent_name = step["agent_name"]
        task_type = step["task_type"]
        # Make a copy so we don't mutate the workflow definition
        parameters = copy.deepcopy(step["parameters"])

        # Resolve parameters that reference previous results
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                ref_agent = value[2:-2]
                # Special handling for SentimentAgent's symbols parameter
                if agent_name == "SentimentAgent" and key == "symbols":
                    ref = value[2:-2]  # e.g., "MarketDataAgent.result"
                    ref_agent = ref.split(".")[0]
                    market_data = results.get(ref_agent).data if ref_agent in results else None
                    print("DEBUG: market_data for SentimentAgent:", market_data)
                    if market_data and isinstance(market_data, list) and len(market_data) > 0:
                        first_row = market_data[0]
                        print("first_row keys and types:")
                        for k in first_row.keys():
                            print(f"  {k!r} (type: {type(k)})")
                        symbols = [k[1] for k in first_row.keys() if isinstance(k, tuple) and len(k) == 2 and str(k[0]).strip().lower() == 'close']
                        # if not symbols:
                            # symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
                        # print("Extracted symbols:", symbols)
                        parameters[key] = symbols
                    else:
                        print("DEBUG: market_data is empty or not a list")
                        parameters[key] = []
                else:
                    # For other dependencies
                    ref = value[2:-2]
                    ref_agent = ref.split(".")[0]
                    parameters[key] = results[ref_agent].data if ref_agent in results else None

        if agent_name == "SentimentAgent":
            print("Symbols being passed to SentimentAgent:", parameters.get("symbols"))

        # Execute the task
        result = await supervisor.agents[agent_name].execute({
            "agent_name": agent_name,
            "task_type": task_type,
            "parameters": parameters,
            "priority": step.get("priority", 0),
            "retries": step.get("retries", 0)
        })
        results[agent_name] = result
        print(f"{agent_name} result:", result.data)

    print_sentiment_results(results["SentimentAgent"].data)
    print_insight_results(results["InsightAgent"].data, visualization_agent)

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

def print_insight_results(insight_data, visualization_agent):
    print("\n=== Insights ===")
    for insight in insight_data:
        print(f"{insight['company']} ({insight['ticker']}):")
        print(f"  Latest Close: {insight['latest_close']}")
        print(f"  Latest Open: {insight['latest_open']}")
        if insight['price_change_pct'] is not None:
            print(f"  Price Change: {insight['price_change_pct']:.2f}% ({insight['trend']})")
        print(f"  Volume: {insight['volume']}")
        print(f"  Overall Sentiment: {insight['overall_sentiment']} (from {insight['headline_count']} headlines)")
        print(f"  Recommendation: {insight['recommendation']}")
        if insight['divergence_flag']:
            print(f"  {insight['divergence_flag']}")
        if insight['top_headline']:
            print(f"  Top Headline: {insight['top_headline']}")
        print(f"  Gemini Insight: {insight.get('llm_insight', '')}")
        print("-" * 40)

    # --- Visualization ---
    df = pd.DataFrame(insight_data)
    visualization_agent.bar_chart_with_labels(
        df, x='company', y='latest_close', title='Latest Close Prices', filename='close_prices_seaborn.png'
    )
    sentiment_counts = df['overall_sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    visualization_agent.pie_chart_with_counts(
        sentiment_counts, label_col='Sentiment', value_col='Count', title='Sentiment Distribution', filename='sentiment_pie_seaborn.png'
    )

async def main():
    supervisor = SupervisorAgent()
    supervisor.register_agent(MarketDataAgent())
    supervisor.register_agent(SentimentAgent(NewsFetcherAdapter()))
    supervisor.register_agent(InsightAgent(None, None))

    workflow = [
        {
            "agent_name": "MarketDataAgent",
            "task_type": "fetch_top_stocks",
            "parameters": {"count": 15},
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

    await run_workflow(supervisor, workflow)

visualization_agent = VisualizationAgent()

if __name__ == "__main__":
    asyncio.run(main())