import streamlit as st
import asyncio
import pandas as pd
import re
from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from utils.news_fetcher import NewsFetcherAdapter
from utils.company_to_ticker import COMPANY_TO_TICKER
from utils.gemini_helpers import get_gemini_insight
import copy

# Page config
st.set_page_config(page_title="FinSight Chat", page_icon="💬", layout="centered")

# Enhanced CSS styling for chat bubbles
st.markdown("""
    <style>
        .chat-bubble {
            padding: 12px 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            width: fit-content;
            max-width: 80%;
            color: #333;
            font-size: 14px;
            line-height: 1.4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .user {
            background-color: #DCF8C6;
            align-self: flex-end;
        }
        .bot {
            background-color: #F1F0F0;
            align-self: flex-start;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .highlight {
            font-weight: bold;
            color: #2c3e50;
        }
        .warning {
            color: #e74c3c;
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize agents
supervisor = SupervisorAgent()
supervisor.register_agent(MarketDataAgent())
supervisor.register_agent(SentimentAgent(NewsFetcherAdapter()))
supervisor.register_agent(InsightAgent(None, None))

def normalize_company_key(name):
    return name.replace(" ", "").upper()

def map_to_tickers(items):
    tickers = []
    normalized_company_map = {normalize_company_key(k): v for k, v in COMPANY_TO_TICKER.items()}
    for item in items:
        key = item.strip().upper()
        if key in COMPANY_TO_TICKER.values():
            tickers.append(key)
        else:
            norm_key = normalize_company_key(item)
            if norm_key in normalized_company_map:
                tickers.append(normalized_company_map[norm_key])
    return tickers

def parse_user_query(query):
    items = re.split(r"[,\s]+", query.strip())
    return [item.upper() for item in items if item]

def extract_tickers_llm(query):
    prompt = (
        "Extract all stock tickers (e.g., AAPL, TSLA, RELIANCE.NS) or company names (e.g., Apple, Tesla, Reliance) "
        f"from the following user query. "
        "Return only a comma-separated list of tickers or company names, no explanation, no extra text.\n"
        f"Query: {query}"
    )
    response = get_gemini_insight(prompt)
    items = [item.strip().upper() for item in response.split(",") if item.strip()]
    return items

def format_insight_results(insights):
    if not insights:
        return "No insights available."
    
    output = ""
    if len(insights) == 1:
        info = insights[0]
        output += f"### {info['company']} ({info['ticker']})\n\n"
        output += f"- **Latest Close**: {info['latest_close']}\n"
        output += f"- **Open**: {info['latest_open']}\n"
        output += f"- **Price Change**: {info['price_change_pct']:.2f}% ({info['trend']})\n"
        output += f"- **Volume**: {info['volume']:,}\n"
        output += f"- **Overall Sentiment**: {info['overall_sentiment']} (from {info['headline_count']} headlines)\n"
        output += f"- **Recommendation**: {info['recommendation']}\n"
        if info.get('divergence_flag'):
            output += f"- **Divergence**: {info['divergence_flag']}\n"
        output += f"- **Top Headline**: {info['top_headline']}\n"
        output += f"- **Gemini Insight**: {info['llm_insight']}\n"
        if info['volume'] < 1_000_000:
            output += "- <span class='warning'>⚠️ Low trading volume, may be illiquid or volatile.</span>\n"
        if abs(info['price_change_pct']) > 5:
            output += "- <span class='warning'>⚠️ High price movement detected today.</span>\n"
        if info.get('headlines'):
            output += "\n**Top News Headlines**:\n"
            for h in info['headlines'][:3]:
                output += f"- {h['headline']} ({h['sentiment']}, score: {h['score']})\n"
    else:
        output += "### Insights for Selected Stocks\n\n"
        for info in insights:
            output += f"\n**{info['company']} ({info['ticker']})**\n"
            output += f"- Latest Close: {info['latest_close']}\n"
            output += f"- Price Change: {info['price_change_pct']:.2f}% ({info['trend']})\n"
            output += f"- Volume: {info['volume']:,}\n"
            output += f"- Overall Sentiment: {info['overall_sentiment']}\n"
            output += f"- Recommendation: {info['recommendation']}\n"
            if info.get('divergence_flag'):
                output += f"- Divergence: {info['divergence_flag']}\n"
    
    return output

async def run_workflow(supervisor, user_tickers):
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
    
    results = {}
    for step in workflow:
        agent_name = step["agent_name"]
        task_type = step["task_type"]
        parameters = copy.deepcopy(step["parameters"])
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                ref_agent = value[2:-2].split(".")[0]
                if agent_name == "SentimentAgent" and key == "symbols":
                    market_data = results.get(ref_agent).data if ref_agent in results else None
                    if market_data and isinstance(market_data, list) and len(market_data) > 0:
                        first_row = market_data[0]
                        symbols = [k[1] for k in first_row.keys() if isinstance(k, tuple) and len(k) == 2 and str(k[0]).strip().lower() == 'close']
                        parameters[key] = symbols
                    else:
                        parameters[key] = []
                else:
                    parameters[key] = results[ref_agent].data if ref_agent in results else None
        
        result = await supervisor.agents[agent_name].execute({
            "agent_name": agent_name,
            "task_type": task_type,
            "parameters": parameters,
            "priority": step.get("priority", 0),
            "retries": step.get("retries", 0)
        })
        results[agent_name] = result
    
    return format_insight_results(results["InsightAgent"].data)

# Streamlit UI
st.title("💹 FinSight Agent Chat")

# Display chat history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    css_class = "user" if role == "user" else "bot"
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble {css_class}">
                <strong>{'You' if role == 'user' else 'FinSight'}:</strong><br>{content}
            </div>
        </div>
    """, unsafe_allow_html=True)

# User input
user_input = st.text_input("Enter company names or tickers (e.g., Apple, TSLA)", key="input")

# Send button
if st.button("Send", use_container_width=True) and user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process query
    user_symbols_raw = extract_tickers_llm(user_input)
    user_tickers = map_to_tickers(user_symbols_raw)
    
    if not user_tickers:
        response = "Sorry, I couldn't find any valid stock tickers in your query."
    else:
        # Run async workflow in Streamlit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(run_workflow(supervisor, user_tickers))
        finally:
            loop.close()
    
    # Add bot response to chat
    st.session_state.messages.append({"role": "bot", "content": response})
    
    # Rerun to update UI
    st.rerun()