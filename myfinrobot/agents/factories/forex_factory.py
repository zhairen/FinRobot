#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇代理统一工厂（完整实现）"""
from typing import Dict, Any
from ..agents.forex_agents import ForexAnalysisAgent, ForexTradingSignalAgent
from ..engine import AgentFactory
from finrobot.engine.data_engine import DataEngine
from finrobot.engine.strategy_engine import StrategyEngine
from ..utils.logger import logger  # 复用项目日志

class ForexAgentFactory(AgentFactory):
    """外汇代理统一工厂（支持分析/交易代理创建）"""
    @staticmethod
    def create_agent(
        agent_type: str,
        data_engine: DataEngine,
        strategy_engine: StrategyEngine
    ) -> Agent:
        """
        创建外汇代理实例
        
        Args:
            agent_type: "analysis"（分析代理）或"trading"（交易代理）
            data_engine: 已初始化的DataEngine实例
            strategy_engine: 已初始化的StrategyEngine实例
            
        Returns:
            Agent: 具体外汇代理实例
        """
        try:
            if agent_type == "analysis":
                logger.info("创建外汇分析代理实例")
                return ForexAnalysisAgent(data_engine, strategy_engine)
            elif agent_type == "trading":
                logger.info("创建外汇交易信号代理实例")
                return ForexTradingSignalAgent(data_engine, strategy_engine)
            else:
                raise ValueError(f"不支持的代理类型：{agent_type}")
        except Exception as e:
            logger.error(f"外汇代理创建失败（类型={agent_type}）：{str(e)}")
            raise