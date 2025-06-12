class Pipeline:
    def __init__(self, agents):
        self.agents = agents

    def run(self):
        market_data = self.agents['MarketDataAgent'].fetch_data()
        sentiment_scores = self.agents['SentimentAgent'].analyze_sentiment(market_data)
        insights = self.agents['InsightAgent'].generate_insights(market_data, sentiment_scores)
        
        if 'VisualizationAgent' in self.agents:
            self.agents['VisualizationAgent'].visualize(insights)

    def add_agent(self, agent_name, agent_instance):
        self.agents[agent_name] = agent_instance

    def remove_agent(self, agent_name):
        if agent_name in self.agents:
            del self.agents[agent_name]