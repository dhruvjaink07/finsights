from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from agents.visualization_agent import VisualizationAgent
from utils.news_fetcher import NewsFetcherAdapter
from utils.company_to_ticker import COMPANY_TO_TICKER
from utils.gemini_helpers import get_gemini_insight  # Add this import
import asyncio
import copy
import pandas as pd
import re
import dotenv
dotenv.load_dotenv()



def normalize_company_key(name):
    return name.replace(" ", "").upper()

def map_to_tickers(items):
    tickers = []
    # Build a normalized mapping for company names
    normalized_company_map = {normalize_company_key(k): v for k, v in COMPANY_TO_TICKER.items()}
    for item in items:
        key = item.strip().upper()
        # Try direct ticker match first
        if key in COMPANY_TO_TICKER.values():
            tickers.append(key)
        else:
            norm_key = normalize_company_key(item)
            if norm_key in normalized_company_map:
                tickers.append(normalized_company_map[norm_key])
    return tickers

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

def print_insight_results(insights, visualization_agent):
    if not insights:
        print("No insights available.")
        return

    if len(insights) == 1:
        info = insights[0]
        print(f"\n=== {info['company']} ({info['ticker']}) ===")
        print(f"Latest Close: {info['latest_close']}")
        print(f"Open: {info['latest_open']}")
        print(f"Price Change: {info['price_change_pct']:.2f}% ({info['trend']})")
        print(f"Volume: {info['volume']}")
        print(f"Overall Sentiment: {info['overall_sentiment']} (from {info['headline_count']} headlines)")
        print(f"Recommendation: {info['recommendation']}")
        if info.get('divergence_flag'):
            print(info['divergence_flag'])
        print(f"Top Headline: {info['top_headline']}")
        print(f"Gemini Insight: {info['llm_insight']}")
        # Add-ons:
        if info['volume'] < 1_000_000:
            print("⚠️ Warning: Low trading volume, may be illiquid or volatile.")
        if abs(info['price_change_pct']) > 5:
            print("⚠️ Warning: High price movement detected today.")
        # Show top 3 headlines if available
        if info.get('headlines'):
            print("\nTop News Headlines:")
            for h in info['headlines'][:3]:
                print(f"- {h['headline']} ({h['sentiment']}, score: {h['score']})")
        # Suggest a related stock (dummy example)
        related = {
            "AAPL": "MSFT",
            "TSLA": "NIO",
            "RELIANCE.NS": "TCS.NS",
            # ...add more
        }
        suggestion = related.get(info['ticker'])
        if suggestion:
            print(f"\nYou may also want to check: {suggestion}")
        print("-" * 40)
    else:
        # --- Multi-stock summary ---
        print("\n=== Insights for Selected Stocks ===")
        for info in insights:
            print(f"\n{info['company']} ({info['ticker']}):")
            print(f"  Latest Close: {info['latest_close']}")
            print(f"  Price Change: {info['price_change_pct']:.2f}% ({info['trend']})")
            print(f"  Volume: {info['volume']}")
            print(f"  Overall Sentiment: {info['overall_sentiment']}")
            print(f"  Recommendation: {info['recommendation']}")
            if info.get('divergence_flag'):
                print(f"  Divergence: {info['divergence_flag']}")
            print("-" * 40)

        # --- Visualization for multiple stocks ---
        df = pd.DataFrame(insights)
        visualization_agent.bar_chart_with_labels(
            df, x='company', y='latest_close', title='Latest Close Prices', filename='close_prices_seaborn.png'
        )
        sentiment_counts = df['overall_sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        visualization_agent.sentiment_pie_chart(
            [{'sentiment': row['Sentiment']} for _, row in sentiment_counts.iterrows()],
            company="All Selected Stocks",
            filename='sentiment_pie_seaborn.png'
        )

    # --- Visualization for single stock ---
    # 1. Sentiment Pie Chart
    if info.get('headlines'):
        visualization_agent.sentiment_pie_chart(
            info['headlines'], info['company'], filename=f"{info['ticker']}_sentiment_pie.png"
        )
        # 2. Sentiment Timeline
        visualization_agent.sentiment_timeline(
            info['headlines'], info['company'], filename=f"{info['ticker']}_sentiment_timeline.png"
        )
    # 3. Candlestick Chart (if mplfinance installed)
    visualization_agent.candlestick_chart(
        info['ticker'], filename=f"{info['ticker']}_candlestick.png", period="5d"
    )
    # 4. Price & Volume Chart (if you have historical data)
    # If you only have one day, skip or fetch more days in MarketDataAgent
    # Example:
    # df_hist = get_historical_df(info['ticker'])  # Implement this if you want
    # if df_hist is not None:
    #     visualization_agent.price_volume_chart(df_hist, info['ticker'], filename=f"{info['ticker']}_price_volume.png")

    print("-" * 40)

def parse_user_query(query):
    # Accept comma/space separated tickers or names, e.g. "AAPL, TSLA" or "Apple, Tesla"
    items = re.split(r"[,\s]+", query.strip())
    # Remove empty strings and uppercase for tickers
    return [item.upper() for item in items if item]

def extract_tickers_llm(query):
    """
    Use Gemini LLM to extract stock tickers from a natural language query.
    Returns a list of tickers (e.g., ["AAPL", "TSLA"]).
    """
    prompt = (
        "Extract all stock tickers (e.g., AAPL, TSLA, RELIANCE.NS) or company names (e.g., Apple, Tesla, Reliance) "
        f"from the following user query. "
        "Return only a comma-separated list of tickers or company names, no explanation, no extra text.\n"
        f"Query: {query}"
    )
    response = get_gemini_insight(prompt)
    # Split by comma, strip whitespace, and filter out empty strings
    items = [item.strip().upper() for item in response.split(",") if item.strip()]
    return items

async def main():
    supervisor = SupervisorAgent()
    supervisor.register_agent(MarketDataAgent())
    supervisor.register_agent(SentimentAgent(NewsFetcherAdapter()))
    supervisor.register_agent(InsightAgent(None, None))

    while True:
        user_query = input("\nAsk your stock question (natural language, or 'exit' to quit):\n> ")
        if user_query.strip().lower() == 'exit':
            print("Goodbye!")
            break

        user_symbols_raw = extract_tickers_llm(user_query)  # LLM returns names/tickers
        user_symbols = map_to_tickers(user_symbols_raw)
        if not user_symbols:
            print("Sorry, I couldn't find any valid stock tickers in your query.")
            continue

        # Map user symbols to actual tickers
        user_tickers = map_to_tickers(user_symbols)
        if not user_tickers:
            print("Sorry, I couldn't map any of the provided symbols to known tickers.")
            continue

        workflow = [
            {
                "agent_name": "MarketDataAgent",
                "task_type": "fetch_specific_stocks",
                "parameters": {"symbols": user_tickers},
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