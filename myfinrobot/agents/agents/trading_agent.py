#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: trading_agent.py
Created Time: 2025-07-10 23:24:35
Author: Coin Lau (jinxinliu@gmail.com)
Description: 交易策略代理，依赖StrategyEngine生成策略并调用大模型生成建议
"""
from typing import Any, Dict
from ..engine.agent_engine import Agent, Task, ModelGateway
from ...engine.strategy_engine import StrategyEngine  # 假设已存在

class TradingStrategyAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        """
        初始化交易策略代理
        
        Args:
            config: 包含StrategyEngine配置的字典（如"strategy_engine_config"）
        """
        # 依赖注入校验（新增）
        if "strategy_engine_config" not in config:
            raise ValueError("TradingStrategyAgent需要strategy_engine_config配置参数")
        self.strategy_engine = StrategyEngine(config["strategy_engine_config"])
        
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        """
        执行交易策略任务
        
        Args:
            task: 包含策略参数的任务对象
            gateway: 大模型网关实例
            
        Returns:
            大模型生成的交易建议
        """
        # 策略准备（使用DataEngine获取数据，示例扩展）
        strategy = self.strategy_engine.get_strategy(task.parameters)
        
        # 生成策略提示（复用prompts中的模板，假设存在）
        from ..prompts import trading_prompt_template  # 新增：引用现有prompts
        prompt = trading_prompt_template.format(
            task_type=task.type,
            parameters=task.parameters,
            strategy_summary=strategy.description
        )
        
        # 调用模型生成结果（使用task中的模型配置）
        return gateway.generate(prompt, task.parameters.get("model_config", {}))