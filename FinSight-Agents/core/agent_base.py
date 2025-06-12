class AgentBase:
    def __init__(self, name):
        self.name = name
        self.is_active = True

    def start(self):
        """Start the agent's operations."""
        if not self.is_active:
            self.is_active = True
            print(f"{self.name} has started.")

    def stop(self):
        """Stop the agent's operations."""
        if self.is_active:
            self.is_active = False
            print(f"{self.name} has stopped.")

    def process(self, data):
        """Process the incoming data. This method should be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

    def get_status(self):
        """Return the current status of the agent."""
        return {
            "name": self.name,
            "is_active": self.is_active
        }