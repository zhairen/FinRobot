#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: finrobot_adapter.py
Created Time: 2025-07-10 23:25:13
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ..engine import Agent, Task, ModelGateway
from .workflow import SingleAssistantRAG  # 复用已有工作流

class FinRobotAdapter(Agent):
    def __init__(self, config: Dict[str, Any]):
        self.agent = SingleAssistantRAG(
            agent_config=config["agent_config"],
            llm_config=config.get("llm_config", {}),
            retrieve_config=config["retrieve_config"]
        )
        
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        # 准备FinRobot任务
        task_config = {
            **task.parameters,
            "model_gateway": gateway
        }
        
        # 执行任务
        self.agent.chat(task.parameters["message"])
        return self.agent.get_result()