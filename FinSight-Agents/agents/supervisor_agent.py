from adk.agent import Agent

class SupervisorAgent(Agent):
    def __init__(self, sub_agents=None ):
        """
        Initializes the SupervisorAgent with optional sub-agents.

        sub_agents: list
            Expected order:
                [0] MarketDataAgent
                [1] SentimentAgent
                [2] InsightAgent
        """
        super().__init__(
            name="SupervisorAgent",
            description="Orchestrates Market, Sentiment, and Insight agents."
        )
        self.sub_agents = sub_agents if sub_agents else []
    
    def run(self):
        """
        Executes the workflow by sequentially calling child agents.

        input_data: dict or None
        returns: final output from InsightAgent
        """
        self._log("SupervisorAgent started")

        # Step 1: Get market data
        self._log("Calling MarketDataAgent")
        market_data = self.sub_agents[0].run(input_data)

        # Step 2: Get sentiment data
        self._log("Calling SentimentAgent")
        sentiment_data = self.sub_agents[1].run(input_data)

        #Step 3: Generate insights
        self._log("Calling InsightAgent")
        insight = self.sub_agents[2].run({
            "market_data": market_data,
            "sentiment_data": sentiment_data
        })

        self._log("Worflow completed")
        return insight
    
    def _log(self, message):
        """
        Logs messages to the console.

        message: str
        """
        print(f"[SupervisorAgent] {message}")
