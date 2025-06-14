from typing import Dict, Any, List
from agents.supervisor_agent import AgentTask
import re
import copy

def resolve_dependencies(task, results):
    resolved = copy.deepcopy(task)
    pattern = re.compile(r"\{\{(.+?)\}\}")
    for k, v in resolved["parameters"].items():
        if isinstance(v, str):
            match = pattern.match(v)
            if match:
                ref = match.group(1)
                agent_name, _ = ref.split(".")
                resolved["parameters"][k] = results.get(agent_name, None)
    return resolved