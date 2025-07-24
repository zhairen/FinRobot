#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇模块集成测试（完整工作流）"""
import pytest
from finrobot.agents.engine.agent_engine import AgentEngine, Task
from finrobot.agents.factories.forex_factory import ForexAgentFactory
from finrobot.engine.data_engine import DataEngine
from finrobot.engine.strategy_engine import StrategyEngine
from finrobot.agents.engine.model_gateways.openai_gateway import OpenAIGateway
from finrobot.utils.logger import setup_logger

# 初始化日志
setup_logger()

# 测试配置（需替换为真实API密钥）
TEST_CONFIG = {
    "alpha_vantage_key": "YOUR_ALPHA_VANTAGE_KEY",
    "oanda_token": "YOUR_OANDA_TOKEN",
    "oanda_account_id": "YOUR_OANDA_ACCOUNT_ID",
    "openai_key": "YOUR_OPENAI_KEY"
}

@pytest.fixture(scope="module")
def forex_dependencies():
    """初始化测试依赖（DataEngine/StrategyEngine/AgentEngine）"""
    # 初始化数据引擎（使用AlphaVantage）
    data_engine = DataEngine(cache_ttl=3600)
    data_engine.set_forex_source(
        source_type="alpha_vantage",
        config={"api_key": TEST_CONFIG["alpha_vantage_key"]}
    )

    # 初始化策略引擎
    strategy_engine = StrategyEngine()

    # 初始化代理引擎
    agent_engine = AgentEngine()
    agent_engine.register_model(
        name="openai",
        gateway=OpenAIGateway(api_key=TEST_CONFIG["openai_key"])
    )
    agent_engine.register_agent_factory(
        agent_type="forex_analysis",
        factory=ForexAgentFactory()
    )
    agent_engine.register_agent_factory(
        agent_type="forex_trading",
        factory=ForexAgentFactory()
    )

    return {
        "data_engine": data_engine,
        "strategy_engine": strategy_engine,
        "agent_engine": agent_engine
    }

def test_forex_analysis_workflow(forex_dependencies):
    """测试外汇分析完整工作流"""
    agent_engine = forex_dependencies["agent_engine"]
    
    # 创建分析任务
    task = Task(
        type="forex_analysis",
        parameters={
            "symbol": "EUR/USD",
            "timeframe": "D",
            "strategy_name": "forex_fundamental",
            "model_config": {"model": "gpt-3.5-turbo"}
        },
        model_type="openai"
    )

    # 执行任务
    result = agent_engine.execute_task(task)
    assert isinstance(result, str), "分析结果应为字符串"
    logger.info(f"外汇分析测试结果：{result[:100]}...")  # 输出前100字符

def test_forex_trading_signal_workflow(forex_dependencies):
    """测试外汇交易信号生成工作流"""
    agent_engine = forex_dependencies["agent_engine"]
    
    # 创建交易任务（使用RSI策略）
    task = Task(
        type="forex_trading",
        parameters={
            "symbol": "AUD/JPY",
            "timeframe": "H4",
            "strategy_name": "forex_rsi",
            "use_llm": False,  # 直接返回信号
            "model_config": {"model": "gpt-3.5-turbo"}
        },
        model_type="openai"
    )

    # 执行任务
    result = agent_engine.execute_task(task)
    assert result in ["BUY", "SELL", "HOLD"], "交易信号应为有效类型"
    logger.info(f"外汇交易信号测试结果：{result}")

def test_oanda_data_source_switch(forex_dependencies):
    """测试OANDA数据源切换"""
    data_engine = forex_dependencies["data_engine"]
    data_engine.set_forex_source(
        source_type="oanda",
        config={
            "access_token": TEST_CONFIG["oanda_token"],
            "account_id": TEST_CONFIG["oanda_account_id"]
        }
    )

    # 获取OANDA数据
    historical_data = data_engine.get_forex_data(
        symbol="GBP/USD",
        timeframe="H1",
        count=100
    )
    assert not historical_data.empty, "OANDA历史数据获取失败"
    logger.info(f"OANDA数据测试：获取到{len(historical_data)}条记录")