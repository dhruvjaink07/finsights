import unittest
from agents.supervisor_agent import SupervisorAgent
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.insight_agent import InsightAgent
from agents.visualization_agent import VisualizationAgent

class TestFinSightAgents(unittest.TestCase):

    def setUp(self):
        self.supervisor_agent = SupervisorAgent()
        self.market_data_agent = MarketDataAgent()
        self.sentiment_agent = SentimentAgent()
        self.insight_agent = InsightAgent()
        self.visualization_agent = VisualizationAgent()

    def test_supervisor_agent_initialization(self):
        self.assertIsInstance(self.supervisor_agent, SupervisorAgent)

    def test_market_data_agent_initialization(self):
        self.assertIsInstance(self.market_data_agent, MarketDataAgent)

    def test_sentiment_agent_initialization(self):
        self.assertIsInstance(self.sentiment_agent, SentimentAgent)

    def test_insight_agent_initialization(self):
        self.assertIsInstance(self.insight_agent, InsightAgent)

    def test_visualization_agent_initialization(self):
        self.assertIsInstance(self.visualization_agent, VisualizationAgent)

    # Additional tests can be added here to test specific functionalities of each agent

if __name__ == '__main__':
    unittest.main()