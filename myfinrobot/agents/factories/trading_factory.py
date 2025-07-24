#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: trading_factory.py
Created Time: 2025-07-10 23:23:05
Author: Coin Lau (jinxinliu@gmail.com)
Description: 交易策略代理工厂，负责创建TradingStrategyAgent实例，支持从agent_library加载预配置
"""
from typing import Dict, Any
from ...agents.agents.trading_agent import TradingStrategyAgent
from ..engine import AgentFactory
from ..utils import load_agent_config  # 复用现有工具函数（假设存在）

class TradingStrategyFactory(AgentFactory):
    def create_agent(self, config: Dict[str, Any]) -> TradingStrategyAgent:
        """
        创建交易策略代理实例
        
        Args:
            config: 代理配置参数，应包含：
                - strategy_engine_config: StrategyEngine初始化配置（必填）
                - 可选参数：从agent_library继承的预配置
        
        Returns:
            TradingStrategyAgent 实例
        """
        # 加载agent_library中的预配置（新增）
        merged_config = load_agent_config("trading_strategy", config)
        
        # 传递合并后的配置创建代理
        return TradingStrategyAgent(merged_config)