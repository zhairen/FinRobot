from typing import Any, Dict
from myfinrobot.agents.agents.analysis_agent import DataAnalysisAgent
from myfinrobot.agents.engine.agent_engine import AgentFactory

class DataAnalysisFactory(AgentFactory):
    def create_agent(self, config: Dict[str, Any]) -> DataAnalysisAgent:
        return DataAnalysisAgent(config)