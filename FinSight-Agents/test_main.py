import streamlit as st
import asyncio
import pandas as pd
import re
from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from agents.visualization_agent import VisualizationAgent
from utils.news_fetcher import NewsFetcherAdapter
from utils.company_to_ticker import COMPANY_TO_TICKER
from utils.gemini_helpers import get_gemini_insight
import copy
import dotenv
import random
import os

dotenv.load_dotenv()

# Page config
st.set_page_config(page_title="FinSight Agent Chat", page_icon="💹", layout="centered")

# Custom CSS (unchanged, included for completeness)
st.markdown("""
    <style>
        body, .stApp {
            background-color: #111827 !important;
        }
        .main {
            background-color: #111827 !important;
        }
        .fin-header {
            text-align: center;
            margin-bottom: 32px;
        }
        .fin-title {
            color: #fff;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        .fin-search-box {
            width: 100%;
            max-width: 500px;
            margin: 0 auto 24px auto;
            display: flex;
            gap: 0.5rem;
        }
        .fin-card {
            background: #181f2a;
            border-radius: 18px;
            padding: 28px 32px 22px 32px;
            margin-bottom: 24px;
            color: #fff;
            box-shadow: 0 4px 24px rgba(0,0,0,0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .fin-card-content {
            flex: 1 1 300px;
        }
        .fin-card-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .fin-card-ticker {
            font-size: 1rem;
            color: #a1a1aa;
            margin-bottom: 0.7rem;
        }
        .fin-card-row {
            display: flex;
            gap: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .fin-card-label {
            color: #a1a1aa;
            font-size: 0.95rem;
        }
        .fin-card-value {
            font-size: 1.05rem;
            font-weight: 500;
        }
        .fin-card-sentiment {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 1.05rem;
        }
        .sentiment-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .sentiment-positive { background: #22c55e; }
        .sentiment-neutral { background: #f59e42; }
        .sentiment-negative { background: #ef4444; }
        .fin-card-price {
            font-size: 2rem;
            font-weight: 700;
            text-align: right;
        }
        .fin-card-change-pos { color: #22c55e; }
        .fin-card-change-neg { color: #ef4444; }
        .fin-card-action {
            margin-top: 10px;
            padding: 6px 18px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1.05rem;
            border: none;
            display: inline-block;
        }
        .action-buy { background: #22c55e; color: #fff; }
        .action-hold { background: #f59e42; color: #fff; }
        .action-avoid { background: #ef4444; color: #fff; }
        @media (max-width: 700px) {
            .fin-card {
                flex-direction: column !important;
                align-items: stretch !important;
                padding: 8px 8px 12px 8px !important;
                margin-bottom: 14px !important;
                min-width: 0 !important;
            }
            .fin-card-content {
                width: 100% !important;
                margin-bottom: 6px !important;
            }
            .fin-card-title {
                font-size: 1rem !important;
                margin-bottom: 0.1rem !important;
            }
            .fin-card-ticker {
                font-size: 0.85rem !important;
                margin-bottom: 0.3rem !important;
            }
            .fin-card-label, .fin-card-value, .fin-card-sentiment {
                font-size: 0.85rem !important;
            }
            .fin-card-row {
                gap: 0.7rem !important;
                margin-bottom: 0.1rem !important;
            }
            .fin-card-price {
                font-size: 1.1rem !important;
                text-align: left !important;
                margin-top: 0 !important;
                margin-bottom: 2px !important;
            }
            .fin-card-action, .fin-card-change-pos, .fin-card-change-neg {
                text-align: left !important;
                margin-top: 0 !important;
                font-size: 0.92rem !important;
            }
            .fin-card > div:last-child {
                width: 100% !important;
                min-width: unset !important;
                margin-top: 2px !important;
            }
        }
        .chat-history {
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #374151;
        }
        .chat-query {
            color: #a1a1aa;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Shimmer loader CSS (unchanged)
bar_widths = [random.randint(65, 100) for _ in range(3)]
st.markdown(f"""
    <style>
    .shimmer-wrapper {{
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin: 0 0 32px 0;
        gap: 12px;
        padding-left: max(env(safe-area-inset-left), 0px);
    }}
    .shimmer-bar:nth-child(1) {{
        width: 100%;
        max-width: 500px;
    }}
    .shimmer-bar:nth-child(2) {{
        width: 60%;
        max-width: 500px;
    }}
    .shimmer-bar:nth-child(3) {{
        width: 40%;
        max-width: 500px;
    }}
    .shimmer-bar {{
        height: 20px;
        border-radius: 8px;
        background: #232b3a;
        position: relative;
        overflow: hidden;
        margin: 0;
    }}
    .shimmer-effect {{
        position: absolute;
        top: 0; left: 0; height: 100%; width: 100%;
        background: linear-gradient(90deg, rgba(35,43,58,0) 0%, rgba(60,70,90,0.25) 50%, rgba(35,43,58,0) 100%);
        animation: shimmer 1.2s infinite;
    }}
    @keyframes shimmer {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    </style>
""", unsafe_allow_html=True)

def shimmer_loader(num_bars=3):
    bars = ""
    for _ in range(num_bars):
        bars += """
        <div class="shimmer-bar">
            <div class="shimmer-effect"></div>
        </div>
        """
    return f'<div class="shimmer-wrapper">{bars}</div>'

# --- Utility Functions (unchanged) ---

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

def get_sentiment_color(sentiment):
    if sentiment.lower() == "positive":
        return "sentiment-positive"
    elif sentiment.lower() == "neutral":
        return "sentiment-neutral"
    else:
        return "sentiment-negative"

def get_action_class(action):
    if action.lower() == "buy":
        return "action-buy"
    elif action.lower() == "hold":
        return "action-hold"
    else:
        return "action-avoid"

def get_action_label(action):
    if action.lower() == "buy":
        return "Buy"
    elif action.lower() == "hold":
        return "Hold"
    else:
        return "Avoid"

def format_card(info):
    sentiment_class = get_sentiment_color(info['overall_sentiment'])
    action_class = get_action_class(info['recommendation'])
    action_label = get_action_label(info['recommendation'])
    price_change = info['price_change_pct']
    price_class = "fin-card-change-pos" if price_change >= 0 else "fin-card-change-neg"
    price_change_str = f"+{price_change:.2f}%" if price_change >= 0 else f"{price_change:.2f}%"
    volume_str = f"{info['volume']/1_000_000:.1f}M" if info['volume'] >= 1_000_000 else f"{info['volume']:,}"
    return f"""
    <div class="fin-card">
        <div class="fin-card-content">
            <div class="fin-card-title">{info['company']}</div>
            <div class="fin-card-ticker">{info['ticker']}</div>
            <div class="fin-card-row">
                <div>
                    <div class="fin-card-label">Volume</div>
                    <div class="fin-card-value">{volume_str}</div>
                </div>
                <div>
                    <div class="fin-card-label">Sentiment</div>
                    <div class="fin-card-sentiment">
                        <span class="sentiment-dot {sentiment_class}"></span>
                        {info['overall_sentiment']}
                    </div>
                </div>
            </div>
        </div>
        <div style="text-align:right;min-width:140px;">
            <div class="fin-card-price">${info['latest_close']}</div>
            <div class="{price_class}" style="font-size:1.1rem;">{price_change_str}</div>
            <div>
                <span class="fin-card-action {action_class}">{action_label}</span>
            </div>
        </div>
    </div>
    """

def format_cards(insights):
    if not insights:
        return "<div style='color:#fff;'>No insights available.</div>"
    cards = ""
    for info in insights:
        cards += format_card(info)
    return cards

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
    return results["InsightAgent"].data

# --- Initialize Session State for Chat History ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Streamlit UI ---

# Header
st.markdown("""
    <div class="fin-header">
        <div class="fin-title">
            <span style="font-size:1.7rem;">📈</span> FinSight Agent Chat
        </div>
    </div>
""", unsafe_allow_html=True)

# Clear History Button
if st.session_state.chat_history:
    if st.button("Clear Chat History", key="clear_history"):
        st.session_state.chat_history = []
        st.experimental_rerun()

# Search box
with st.form(key="fin_form"):
    col1, col2 = st.columns([5,1])
    with col1:
        user_input = st.text_input(
            "Enter company names or tickers (e.g., AAPL, MSFT, TSLA)",
            key="input",
            label_visibility="collapsed",
            placeholder="Enter company names or tickers (e.g., AAPL, MSFT, TSLA)"
        )
    with col2:
        submit = st.form_submit_button("🔎 Analyze", use_container_width=True)

# Initialize agents
supervisor = SupervisorAgent()
supervisor.register_agent(MarketDataAgent())
supervisor.register_agent(SentimentAgent(NewsFetcherAdapter()))
supervisor.register_agent(InsightAgent(None, None))
visualization_agent = VisualizationAgent()

# Process new query
if submit and user_input:
    user_symbols_raw = extract_tickers_llm(user_input)
    user_tickers = map_to_tickers(user_symbols_raw)
    if not user_tickers:
        st.warning("Sorry, I couldn't find any valid stock tickers in your query.")
    else:
        # Show shimmer loader while processing
        shimmer_placeholder = st.empty()
        shimmer_placeholder.html(shimmer_loader(3))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            insights = loop.run_until_complete(run_workflow(supervisor, user_tickers))
            # Store visualization paths
            visualization_paths = []
            if insights:
                if len(insights) == 1:
                    info = insights[0]
                    # Sentiment Pie Chart
                    if info.get('headlines'):
                        pie_path = os.path.join(visualization_agent.save_dir, f"{info['ticker']}_sentiment_pie.png")
                        visualization_agent.sentiment_pie_chart(info['headlines'], info['company'], filename=f"{info['ticker']}_sentiment_pie.png")
                        if os.path.exists(pie_path):
                            visualization_paths.append(('Sentiment Distribution', pie_path))
                    # Sentiment Timeline
                    if info.get('headlines'):
                        timeline_path = os.path.join(visualization_agent.save_dir, f"{info['ticker']}_sentiment_timeline.png")
                        visualization_agent.sentiment_timeline(info['headlines'], info['company'], filename=f"{info['ticker']}_sentiment_timeline.png")
                        if os.path.exists(timeline_path):
                            visualization_paths.append(('Sentiment Timeline', timeline_path))
                    # Candlestick Chart
                    candle_path = os.path.join(visualization_agent.save_dir, f"{info['ticker']}_candlestick.png")
                    visualization_agent.candlestick_chart(info['ticker'], filename=f"{info['ticker']}_candlestick.png", period="5d")
                    if os.path.exists(candle_path):
                        visualization_paths.append(('Candlestick Chart', candle_path))
                else:
                    # Multi-stock visualizations
                    df = pd.DataFrame(insights)
                    bar_path = os.path.join(visualization_agent.save_dir, "close_prices_seaborn.png")
                    pie_path = os.path.join(visualization_agent.save_dir, "sentiment_pie_seaborn.png")
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
                    if os.path.exists(bar_path):
                        visualization_paths.append(('Latest Close Prices', bar_path))
                    if os.path.exists(pie_path):
                        visualization_paths.append(('Sentiment Distribution', pie_path))
            # Store in chat history
            st.session_state.chat_history.append({
                'query': user_input,
                'insights': insights,
                'visualization_paths': visualization_paths
            })
        finally:
            loop.close()
        shimmer_placeholder.empty()

# Display Chat History
if st.session_state.chat_history:
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    # st.markdown("### Chat History")
    for entry in reversed(st.session_state.chat_history):  # Show newest first
        st.markdown(f'<div class="chat-query">Query: {entry["query"]}</div>', unsafe_allow_html=True)
        st.markdown(format_cards(entry['insights']), unsafe_allow_html=True)
        for caption, path in entry['visualization_paths']:
            if os.path.exists(path):
                st.image(path, caption=caption, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)