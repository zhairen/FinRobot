#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: finrobot_adapter.py
Created Time: 2025-07-10 23:25:13
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from typing import Any, Dict
from ..engine.agent_engine import Agent, Task, ModelGateway
from ..workflow import SingleAssistantRAG  # 复用已有工作流

class FinRobotAdapter(Agent):
    def __init__(self, config: Dict[str, Any]):
        # 从配置中解析RAG参数（如向量数据库配置）
        self.agent = SingleAssistantRAG(
            agent_config=config["agent_config"],  # 来自agent_library的配置
            llm_config=config.get("llm_config", {}),  # 大模型参数（如model/temperature）
            retrieve_config=config["retrieve_config"],  # RAG检索配置（如向量库路径）
        )

    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        # 1. 准备任务上下文（可扩展添加DataEngine数据）
        context = {
            "user_message": task.parameters["message"],
            "historical_data": task.parameters.get("historical_data", {})
        }
        
        # 2. 执行RAG对话流程
        self.agent.chat(context["user_message"])
        
        # 3. 获取并格式化结果（可添加后处理逻辑）
        raw_result = self.agent.get_result()
        return self._postprocess_result(raw_result)

    def _postprocess_result(self, raw_result: str) -> str:
        # 示例：添加结果校验/结构化转换
        if "ERROR" in raw_result:
            raise ValueError(f"模型返回异常：{raw_result}")
        return raw_result.strip()