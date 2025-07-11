#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: analysis_agent.py
Created Time: 2025-07-10 23:23:58
Author: Coin Lau (jinxinliu@gmail.com)
Description: 数据分析代理，依赖DataEngine获取数据并调用大模型生成分析报告
"""
from typing import Any, Dict
from ..engine.agent_engine import Agent, Task, ModelGateway
from ...engine.data_engine import DataEngine  # 假设已存在

class DataAnalysisAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据分析代理
        
        Args:
            config: 包含DataEngine配置的字典（如"data_engine_config"）
        """
        # 依赖注入校验（新增）
        if "data_engine_config" not in config:
            raise ValueError("DataAnalysisAgent需要data_engine_config配置参数")
        self.data_engine = DataEngine(config["data_engine_config"])
        
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        """
        执行数据分析任务
        
        Args:
            task: 包含数据参数的任务对象
            gateway: 大模型网关实例
            
        Returns:
            大模型生成的分析报告
        """
        # 数据准备（使用DataEngine获取数据）
        data = self.data_engine.get_data(task.parameters)
        
        # 生成分析提示（复用prompts中的模板，假设存在）
        from ..prompts import analysis_prompt_template  # 新增：引用现有prompts
        prompt = analysis_prompt_template.format(
            task_type=task.type,
            parameters=task.parameters,
            data_summary=data.head(5)  # 假设data是pandas DataFrame
        )
        
        # 调用模型生成结果（使用task中的模型配置）
        return gateway.generate(prompt, task.parameters.get("model_config", {}))