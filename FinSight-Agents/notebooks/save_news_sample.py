import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.news_fetcher import fetch_and_process_news

symbols = ["RELIANCE", "TCS", "HDFCBANK"]
all_articles = []
for symbol in symbols:
    articles = fetch_and_process_news(symbol, num_articles=10)
    for article in articles:
        article['symbol'] = symbol
        all_articles.append(article)

df = pd.DataFrame(all_articles)
df.to_csv("data/processed/news_sample.csv", index=False)
print("Saved news articles for sentiment model testing.")