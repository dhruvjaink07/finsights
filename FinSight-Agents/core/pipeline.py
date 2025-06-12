from typing import Dict, Any, List
from agents.supervisor_agent import AgentTask

def resolve_dependencies(task: AgentTask, results: Dict[str, Any]) -> Dict:
    """Resolve template strings in parameters using previous results"""
    resolved_params = {}
    for key, value in task.parameters.items():
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            ref = value[2:-2].strip()
            resolved_params[key] = results.get(ref)
        else:
            resolved_params[key] = value
    return resolved_params