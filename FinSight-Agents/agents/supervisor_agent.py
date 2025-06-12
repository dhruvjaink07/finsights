import asyncio
import logging
from typing import Dict, List
from dataclasses import dataclass
from core.agent_base import BaseAgent, AgentResult

@dataclass
class AgentTask:
    agent_name: str
    task_type: str
    parameters: Dict
    priority: int = 1
    retries: int = 0

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupervisorAgent")
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.max_retries = 3

    def register_agent(self, agent: BaseAgent):
        """Register subordinate agents"""
        if not isinstance(agent, BaseAgent):
            raise ValueError("Agent must inherit from BaseAgent")
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    async def add_task(self, task: AgentTask):
        """Add task to processing queue"""
        await self.task_queue.put((-task.priority, task))  # Negative for proper priority

    async def execute_workflow(self, workflow: List[Dict]) -> Dict[str, AgentResult]:
        """Execute a predefined workflow"""
        # Add all workflow tasks to queue
        for task_config in workflow:
            task = AgentTask(**task_config)
            await self.add_task(task)

        # Process tasks
        return await self._process_tasks()

    async def _process_tasks(self) -> Dict[str, AgentResult]:
        """Process all tasks in queue"""
        results = {}
        while not self.task_queue.empty():
            _, task = await self.task_queue.get()
            agent = self.agents.get(task.agent_name)
            
            if not agent:
                self.logger.error(f"Agent {task.agent_name} not registered")
                continue

            result = await self._execute_with_retry(agent, task)
            results[f"{task.agent_name}:{task.task_type}"] = result

            # Handle task dependencies
            if result.success and hasattr(agent, 'get_dependent_tasks'):
                dependent_tasks = agent.get_dependent_tasks(task, result.data)
                for dep_task in dependent_tasks:
                    await self.add_task(dep_task)

        return results

    async def _execute_with_retry(self, agent: BaseAgent, task: AgentTask) -> AgentResult:
        """Execute task with retry logic"""
        for attempt in range(task.retries + 1):
            try:
                result = await agent.execute({
                    'task_type': task.task_type,
                    'parameters': task.parameters
                })
                
                if result.success:
                    return result
                
                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {task.agent_name}: {result.error}"
                )
            except Exception as e:
                self.logger.error(
                    f"Exception in {task.agent_name} (attempt {attempt + 1}): {str(e)}"
                )
                result = AgentResult(success=False, data=None, error=str(e))

            if attempt < task.retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return result

    async def execute(self, task: Dict) -> AgentResult:
        """Main execution point for when Supervisor is used as an agent"""
        workflow = task.get('workflow', [])
        results = await self.execute_workflow(workflow)
        return AgentResult(success=True, data=results)