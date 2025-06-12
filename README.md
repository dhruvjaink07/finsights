# FinSight Agents 🧠📈

Multi-Agent Financial Insight System powered by Google Cloud + ADK

A collaborative multi-agent system that fetches real-time market data, analyzes trends, evaluates sentiment from news, and produces actionable financial insights. Built with the Agent Development Kit (ADK) and integrated with Google Cloud services like BigQuery and Vertex AI.

---

## 🧩 Problem Statement

In the fast-paced world of financial markets, extracting and synthesizing data-driven insights requires significant time and expertise. Investors and analysts often juggle data from multiple sources — prices, indicators, news, and reports — which slows down decision-making.

FinSight Agents automates this process using a multi-agent system that:

* Collects live market data
* Scores real-time sentiment from financial news
* Runs financial analytics and indicators
* Generates AI-powered summaries and charts

---

## 🚀 How It Works

The system is orchestrated through the Agent Development Kit (ADK), where each agent plays a specialized role in the pipeline:

| Agent                            | Role                                                              |
| -------------------------------- | ----------------------------------------------------------------- |
| 🧠 SupervisorAgent               | Orchestrates all other agents                                     |
| 📊 MarketDataAgent               | Fetches real-time stock prices and indicators, stores in BigQuery |
| 🗞️ SentimentAgent               | Analyzes latest news sentiment using Gemini or VADER              |
| 📈 InsightAgent                  | Synthesizes outputs from data + sentiment into insights           |
| 📉 VisualizationAgent (Optional) | Generates graphs using Plotly or Looker                           |

---

## 🛠️ Tech Stack

| Tool                        | Purpose                       |
| --------------------------- | ----------------------------- |
| Agent Development Kit (ADK) | Multi-agent orchestration     |
| Python                      | Agent implementation          |
| BigQuery                    | Data storage and querying     |
| Vertex AI / Gemini          | LLM-driven summaries          |
| Plotly / Looker Studio      | Charts and dashboards         |
| Google Search API           | For real-time news collection |

---

## 📂 Project Structure

```bash
FinSight-Agents/
│
├── agents/
│   ├── supervisor_agent.py
│   ├── market_data_agent.py
│   ├── sentiment_agent.py
│   ├── insight_agent.py
│
├── utils/
│   └── bigquery_helpers.py
│
├── data/
│   └── raw_stock_data.csv
│
├── main.py
├── requirements.txt
└── README.md
```

---

## 🧪 Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/finsight-agents.git
cd finsight-agents
```

2. Create a virtual environment:

```bash
python -m venv env
source env/bin/activate  # or .\env\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up Google Cloud credentials for BigQuery & Gemini (if used).

---

## 💡 Example Output

“Tesla dropped 4.2% in the last 3 days, with negative sentiment in the media due to layoffs. RSI indicates oversold. Recommendation: wait for reversal pattern.”

(Visual charts + AI-generated summary shown in demo)

---

## 🎥 Demo

Link: \[YouTube/Vimeo demo link here]

---

## 🧑‍💻 Team Members

* Dhruv Jain – SupervisorAgent, GitHub & ADK architecture
* Tanish – Market Data + BigQuery
* Fawaz – Sentiment Agent + Testing
* Tahab – Insight Agent + Docs + Dashboard

---

## 📜 License

MIT License
