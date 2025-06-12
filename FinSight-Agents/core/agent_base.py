from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional

@dataclass
class AgentResult:
    success: bool
    data: Any
    error: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")

    @abstractmethod
    async def execute(self, task: Dict) -> AgentResult:
        """All agents must implement this async execute method"""
        pass

    async def health_check(self) -> bool:
        """Default health check implementation"""
        return True