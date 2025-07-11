#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: analysis_agent.py
Created Time: 2025-07-10 23:23:58
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ..engine import Agent, Task, ModelGateway
from finrobot.data_engine import DataEngine  # 假设已存在

class DataAnalysisAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        self.data_engine = DataEngine(config)
        
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        # 数据准备
        data = self.data_engine.get_data(task.parameters)
        
        # 生成分析提示
        prompt = f"""
        执行数据分析任务：
        任务类型: {task.type}
        参数: {task.parameters}
        数据摘要: {data.head(5)}
        请提供详细分析报告...
        """
        
        # 使用模型生成分析结果
        return gateway.generate(prompt, task.parameters.get("model_config", {}))