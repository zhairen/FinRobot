#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇代理实现（分析+交易）"""
from ..engine import Agent, Task, ModelGateway
from finrobot.engine.data_engine import DataEngine
from finrobot.engine.strategy_engine import StrategyEngine
from ..utils.logger import logger  # 复用项目日志

class ForexAnalysisAgent(Agent):
    def __init__(self, data_engine: DataEngine, strategy_engine: StrategyEngine):
        self.data_engine = data_engine
        self.strategy_engine = strategy_engine

    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        try:
            # 1. 获取数据
            historical_data = self.data_engine.get_forex_data(
                symbol=task.parameters["symbol"],
                timeframe=task.parameters["timeframe"]
            )
            economic_events = self.data_engine.get_forex_data(
                symbol=task.parameters["symbol"],
                data_type="economic_events"
            )

            # 2. 执行策略
            analysis_result = self.strategy_engine.execute_forex_analysis(
                strategy_name=task.parameters["strategy_name"],
                historical_data=historical_data,
                economic_events=economic_events,
                symbol=task.parameters["symbol"]
            )

            # 3. 生成大模型提示
            prompt = f"""分析以下外汇数据：{analysis_result}，生成专业分析报告。"""
            return gateway.generate(prompt, task.parameters.get("model_config", {}))
        except Exception as e:
            logger.error(f"外汇分析代理执行失败：{str(e)}")
            raise

class ForexTradingSignalAgent(Agent):
    def __init__(self, data_engine: DataEngine, strategy_engine: StrategyEngine):
        self.data_engine = data_engine
        self.strategy_engine = strategy_engine

    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        try:
            # 1. 获取数据
            historical_data = self.data_engine.get_forex_data(
                symbol=task.parameters["symbol"],
                timeframe=task.parameters["timeframe"]
            )

            # 2. 执行策略
            quant_result = self.strategy_engine.execute_forex_quant(
                strategy_name=task.parameters["strategy_name"],
                historical_data=historical_data,
                symbol=task.parameters["symbol"],
                interest_rates=task.parameters["interest_rates"]
            )

            # 3. 生成结果（直接信号或LLM优化）
            if task.parameters.get("use_llm", True):
                prompt = f"""根据以下交易信号：{quant_result}，生成交易建议。"""
                return gateway.generate(prompt, task.parameters.get("model_config", {}))
            else:
                return quant_result["last_signal"]
        except Exception as e:
            logger.error(f"外汇交易代理执行失败：{str(e)}")
            raise

class ForexAgentFactory:
    """统一外汇代理工厂"""
    @staticmethod
    def create_agent(
        agent_type: str,
        data_engine: DataEngine,
        strategy_engine: StrategyEngine
    ) -> Agent:
        if agent_type == "analysis":
            return ForexAnalysisAgent(data_engine, strategy_engine)
        elif agent_type == "trading":
            return ForexTradingSignalAgent