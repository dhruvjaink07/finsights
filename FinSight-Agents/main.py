# FinSight Agents Main Entry Point

from agents.supervisor_agent import SupervisorAgent

class DummyAgent:
    def __init__(self, name):
        self.name = name

    def run(self, input_data=None):
        print(f"[{self.name}] Running...")
        return f"{self.name} result"

if __name__ == "__main__":
    # Create SupervisorAgent with mock agents
    supervisor = SupervisorAgent(sub_agents=[
        DummyAgent("MarketDataAgent"),
        DummyAgent("SentimentAgent"),
        DummyAgent("InsightAgent")
    ])

    # Run the full workflow
    result = supervisor.run()
    print("✅ Final Output:", result)