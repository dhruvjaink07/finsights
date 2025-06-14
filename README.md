# FinSight Agents 🧠📈

**Multi-Agent Financial Insight System powered by Google Cloud + ADK**

A collaborative multi-agent system that fetches real-time market data, analyzes trends, evaluates sentiment from news, and produces actionable financial insights. Built with the Agent Development Kit (ADK) and integrated with Google Cloud services like BigQuery and Vertex AI.

---

## 🚀 Project Overview

FinSight Agents is a robust, extensible multi-agent system that automates financial insight generation by:

- Collecting live market data for any mix of Indian and global stocks
- Dynamically extracting and passing ticker symbols between agents
- Scoring real-time sentiment from financial news using company names
- Synthesizing actionable insights for every stock, even if no news is found
- Generating clear, company-wise summaries and visualizations (bar, pie, candlestick, and technical indicators)

---

## 🧩 Problem Statement

In the fast-paced world of financial markets, extracting and synthesizing data-driven insights requires significant time and expertise. Investors and analysts often juggle data from multiple sources — prices, indicators, news, and reports — which slows down decision-making.

---

## 🏗️ Architecture

| Agent                       | Role                                                                 |
|-----------------------------|----------------------------------------------------------------------|
| 🧠 SupervisorAgent           | Orchestrates all other agents and resolves dependencies dynamically  |
| 📊 MarketDataAgent           | Fetches real-time stock prices (via yfinance) for any tickers        |
| 🗞️ SentimentAgent            | Analyzes latest news sentiment using NewsAPI + VADER (or Gemini)     |
| 📈 InsightAgent              | Aggregates market and sentiment data into per-stock insights         |
| 📉 VisualizationAgent        | Generates graphs (bar, pie, candlestick, technical indicators)       |

- **Dynamic symbol extraction:** The workflow automatically extracts tickers from market data and passes them to downstream agents.
- **Global & Indian stock support:** Add or remove any tickers in one place; the pipeline adapts automatically.
- **Graceful handling:** If no news is found for a stock, the system still generates an insight with "No news".
- **Rich visualizations:** Candlestick charts with moving averages, Bollinger Bands, RSI, plus bar and pie charts for comparison.

---

## 🛠️ Tech Stack

- **Python** (asyncio, pandas, requests, etc.)
- **Agent Development Kit (ADK)** for agent orchestration
- **Google Cloud BigQuery** (Sandbox, CSV upload)
- **yfinance** for market data
- **NewsAPI** for news headlines
- **VADER / NLTK** for sentiment analysis
- **mplfinance, seaborn, matplotlib** for visualization
- **python-dotenv** for secrets management

---

## 📂 Project Structure

```
FinSight-Agents/
│
├── main.py                      # Entry point: runs SupervisorAgent and workflow
├── requirements.txt             # Python dependencies
├── .env                         # Secrets (API keys, not in git)
│
├── agents/                      # All agent classes
│   ├── supervisor_agent.py
│   ├── market_data_agent.py
│   ├── sentiment_agent.py
│   ├── insight_agent.py
│   └── visualization_agent.py
│
├── core/                        # Agent base classes and pipeline logic
│
├── utils/                       # Helper modules (BigQuery, yfinance, news, etc.)
│
├── data/
│   ├── processed/               # Output CSVs and generated charts
│   └── schemas/                 # BigQuery table schemas (JSON)
│
├── notebooks/                   # Jupyter notebooks and scripts for testing
│
├── tests/                       # Unit tests
│
└── README.md
```

---

## ⚡ Quickstart

1. **Clone the repo and install dependencies**
    ```sh
    git clone https://github.com/dhruvjaink07/finsights.git
    cd FinSight-Agents
    pip install -r requirements.txt
    ```

2. **Set up your `.env` file**
    ```
    NEWSAPI_KEY=your_newsapi_key_here
    GEMINI_API_KEY=your_gemini_key
    ```

3. **(Optional) Fetch and save stock/news data**
    ```sh
    python notebooks/init_bigquery.py      # Fetches stock data, saves as CSV
    python notebooks/save_news_sample.py   # Fetches news, saves as CSV
    ```

4. **(Optional) Upload CSVs to BigQuery (Sandbox)**
    - Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
    - Create dataset/table if needed
    - Upload CSVs via the web UI

5. **Run the agent workflow**
    ```sh
    python main.py
    ```

---

## 💬 Usage: Example Prompts

When prompted, you can type natural language queries such as:

- `Apple`
- `Show me insights on Tata Motors`
- `Apple and Microsoft`
- `GOOGLE, Apple Latest insights`
- `Insights on Tata Motors and Tesla`
- `What’s happening with Tesla this week?`
- `Should I buy or sell Apple?`
- `exit` or `quit` to stop

---

## 🖼️ Output

- **Text summaries**: Price, trend, volume, sentiment, news, and recommendations for each stock.
- **Charts**: Bar and pie charts for comparison, candlestick charts with technical indicators (moving averages, Bollinger Bands, RSI) for each stock.
- **All charts and outputs are saved in `data/processed/`**.

---

## 🧪 Testing

- Run all tests:
    ```sh
    pytest tests/
    ```

---

## 📝 Contributing

- Add new agents or tools in the appropriate folders.
- Use `.env` for all secrets and API keys.
- Write or update tests for new features.
- Document your changes in the README or as docstrings.

---

## 📅 Hackathon Timeline

- **June 11–13:** MarketDataAgent, BigQuery integration, news fetcher, agent scaffolding
- **June 14:** SentimentAgent (news + sentiment analysis)
- **June 15+:** InsightAgent, visualization, error handling, demo, docs

---

## 📈 Next Steps

- Enhance InsightAgent with more advanced analytics or recommendations
- Integrate additional data sources or indicators
- Add more visualizations and dashboards
- Expand test coverage and polish documentation for demo/submission

---

## 🙌 Team

- Dhruv, Tanish, Fawaz, Tahab

---

**Let’s build the future of financial insights, together!**
