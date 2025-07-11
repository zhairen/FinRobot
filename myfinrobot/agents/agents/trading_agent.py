#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: trading_agent.py
Created Time: 2025-07-10 23:24:35
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ..engine import Agent, Task, ModelGateway
from finrobot.strategy_engine import StrategyEngine  # 假设已存在

class TradingStrategyAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        self.strategy_engine = StrategyEngine(config)
        
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        # 策略准备
        strategy = self.strategy_engine.get_strategy(task.parameters)
        
        # 生成策略提示
        prompt = f"""
        执行交易策略任务：
        任务类型: {task.type}
        参数: {task.parameters}
        策略摘要: {strategy.description}
        请生成交易信号和风险管理建议...
        """
        
        # 使用模型生成策略结果
        return gateway.generate(prompt, task.parameters.get("model_config", {}))