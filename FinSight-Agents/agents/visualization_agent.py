import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import mplfinance as mpf
    HAS_MPLFINANCE = True
except ImportError:
    HAS_MPLFINANCE = False

class VisualizationAgent:
    def __init__(self, save_dir="data/processed"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def bar_chart_with_labels(self, data: pd.DataFrame, x, y, title=None, filename='bar_chart.png', sort=True, palette='viridis'):
        plt.figure(figsize=(10, 6))
        plot_data = data.copy()
        if sort:
            plot_data = plot_data.sort_values(by=y, ascending=False)
        ax = sns.barplot(data=plot_data, x=x, y=y, hue=x, palette=palette, legend=False)
        plt.title(title or f"{y} by {x}")
        plt.ylabel(y)
        plt.xlabel(x)
        plt.xticks(rotation=30)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=9, color='black', xytext=(0, 5), textcoords='offset points')
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Enhanced bar chart saved to {save_path}")

    def sentiment_pie_chart(self, sentiments, company, filename='sentiment_pie.png'):
        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for s in sentiments:
            counts[s['sentiment']] = counts.get(s['sentiment'], 0) + 1
        plt.figure(figsize=(5,5))
        plt.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', colors=['#4caf50', '#9e9e9e', '#f44336'])
        plt.title(f"Sentiment Distribution for {company}")
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Enhanced pie chart saved to {save_path}")

    def price_volume_chart(self, df: pd.DataFrame, ticker, filename='price_volume.png'):
        if 'Date' not in df.columns:
            print("No Date column for price/volume chart.")
            return
        fig, ax1 = plt.subplots(figsize=(8,4))
        ax1.bar(df['Date'], df['Volume'], color='lightblue', alpha=0.6, label='Volume')
        ax2 = ax1.twinx()
        ax2.plot(df['Date'], df['Close'], color='navy', marker='o', label='Close Price')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Volume')
        ax2.set_ylabel('Close Price')
        plt.title(f"{ticker} - Price & Volume")
        fig.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Price & volume chart saved to {save_path}")

    def candlestick_chart(self, ticker, filename='candlestick.png', period="5d"):
        if not HAS_MPLFINANCE:
            print("mplfinance not installed, skipping candlestick chart.")
            return
        import yfinance as yf
        df = yf.download(ticker, period=period, interval="1d")
        if df.empty:
            print("No data for candlestick chart.")
            return

        # Handle MultiIndex columns (as returned by yfinance for multiple tickers or some single-ticker queries)
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df = df.xs(ticker, axis=1, level=1, drop_level=False)
                df.columns = [col[0] for col in df.columns]
            except Exception:
                df.columns = ['_'.join(col).strip('_') for col in df.columns.values]
                ohlc_cols = [f"{col}_{ticker}" for col in ['Open', 'High', 'Low', 'Close', 'Volume']]
                if all(col in df.columns for col in ohlc_cols):
                    df = df[ohlc_cols]
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        # Now ensure we have the right columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col not in df.columns:
                print(f"No '{col}' column for candlestick chart.")
                return

        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric, errors='coerce')
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        if df.empty:
            print("No valid OHLC data for candlestick chart after cleaning.")
            return

        # Add moving averages (optional)
        mavs = (3,) if len(df) >= 3 else None

        save_path = os.path.join(self.save_dir, filename)
        mpf.plot(
            df,
            type='candle',
            style='yahoo',
            title=f"{ticker} - Last {period}",
            volume=True,
            mav=mavs,
            figsize=(10, 6),
            tight_layout=True,
            savefig=save_path,
            datetime_format='%b %d'
        )
        print(f"Enhanced candlestick chart saved to {save_path}")

    def sentiment_timeline(self, sentiments, company, filename='sentiment_timeline.png'):
        # Expects a list of dicts with 'score' and 'headline'
        if not sentiments:
            print("No sentiment data for timeline.")
            return
        scores = [s['score'] for s in sentiments]
        headlines = [s['headline'][:40] + "..." if len(s['headline']) > 40 else s['headline'] for s in sentiments]
        plt.figure(figsize=(8, 3))
        plt.plot(range(1, len(scores)+1), scores, marker='o', color='purple')
        plt.xticks(range(1, len(scores)+1), headlines, rotation=45, ha='right', fontsize=8)
        plt.title(f"Sentiment Scores Timeline for {company}")
        plt.ylabel("Sentiment Score")
        plt.xlabel("Headline")
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Sentiment timeline chart saved to {save_path}")

# Standalone test
# if __name__ == "__main__":
#     df = pd.DataFrame({
#         'Stock': ['AAPL', 'GOOGL', 'TSLA'],
#         'latest_close': [196.4, 174.6, 325.3],
#         'Volume': [51362400, 27641100, 128495300],
#         'Date': pd.date_range(end=pd.Timestamp.today(), periods=3),
#         'Close': [196.4, 174.6, 325.3]
#     })
#     va = VisualizationAgent()
#     va.bar_chart_with_labels(df, x='Stock', y='latest_close', title="Latest Close Prices")
#     va.price_volume_chart(df, ticker='AAPL')