import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import google.generativeai as genai

class SentimentAgent:
    def __init__(self, use_gemini=True, gemini_api_key=None):
        self.use_gemini = use_gemini
        if use_gemini and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        else:
            self.sia = SentimentIntensityAnalyzer()

    def fetch_news(self, query, api_key):
        """
        Fetches the latest English news headlines for a given stock/analytics query using NewsAPI.
        Returns a list of headline strings.
        """
        # Make the query more specific to stock analytics (modify for different use cases)
        search_query = f"{query} stock analysis"
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={search_query}&"
            f"language=en&"
            f"sortBy=publishedAt&"
            f"apiKey={api_key}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching news: {response.status_code}")
            return []
        articles = response.json().get("articles", [])
        # Filter out non-English headlines
        headlines = []
        for a in articles[:10]:
            title = a["title"]
        # Simple check: skip if contains non-ASCII (not perfect, but helps)
            if all(ord(c) < 128 for c in title):
                headlines.append(title)
        return headlines[:5]

    def analyze_sentiment(self, headlines):
        """
        Analyzes the sentiment of a list of headlines.
        Returns a list of dicts with headline, sentiment label, and score.
        """
        if self.use_gemini:
            prompt = (
                "Analyze the sentiment of the following news headlines about a stock:\n\n"
            )
            for i, headline in enumerate(headlines, 1):
                prompt += f"{i}. {headline}\n"
            prompt += (
                "\nReturn the result as a JSON list like:\n"
                '[{"headline": "...", "sentiment": "Positive/Negative/Neutral", "score": 0.0-1.0}]\n'
            )
            response = self.gemini_model.generate_content(prompt)
            # Try to extract JSON from the response
            import json, re
            match = re.search(r"\[.*\]", response.text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception as e:
                    print("Error parsing Gemini response:", e)
                    return []
            else:
                print("No JSON found in Gemini response.")
                return []
        else:
            results = []
            for headline in headlines:
                score = self.sia.polarity_scores(headline)
                label = (
                    "Positive" if score["compound"] > 0.05 else
                    "Negative" if score["compound"] < -0.05 else
                    "Neutral"
                )
                results.append({
                    "headline": headline,
                    "sentiment": label,
                    "score": round(score["compound"], 2)
                })
            return results

if __name__ == "__main__":
    NEWSAPI_KEY = "14a95236d3f6490d862abc99e806066c"
    GEMINI_API_KEY = "AIzaSyB6hEU0c3fzSPUPQjOcutADrYFjXtnsqFU"
    STOCK_QUERY = "AAPL"

    # Set use_gemini=True to use Gemini, False for VADER
    agent = SentimentAgent(use_gemini=True, gemini_api_key=GEMINI_API_KEY)
    news_headlines = agent.fetch_news(STOCK_QUERY, NEWSAPI_KEY)
    if news_headlines:
        sentiment_results = agent.analyze_sentiment(news_headlines)
        for result in sentiment_results:
            print(result)
    else:
        print("No news headlines found.")