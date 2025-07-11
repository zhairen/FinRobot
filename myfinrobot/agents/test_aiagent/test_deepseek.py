#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: register_deepseek.py
Created Time: 2025-07-15 14:35:00
Author: Coin Lau (jinxinliu@gmail.com)
Description: 注册DeepSeek模型网关并执行任务示例
"""
#import sys
#from pathlib import Path

# 添加项目根路径到sys.path（关键修正）
#sys.path.append(str(Path(__file__).parent.parent.parent.parent))  # 定位到myfinrobot的父目录

from myfinrobot.agents.engine.agent_engine import AgentEngine, Task
from myfinrobot.agents.engine.model_gateways.deepseek_gateway import DeepSeekGateway
from myfinrobot.agents.factories.analysis_factory import DataAnalysisFactory

# 初始化引擎
engine = AgentEngine()

# 注册DeepSeek模型网关（关键步骤）
engine.register_model(
    name="deepseek",  # 与Task.model_type对应
    gateway=DeepSeekGateway(api_key="your_deepseek_api_key")
)

# 注册数据分析代理工厂（已有代码）
engine.register_agent_factory(
    agent_type="data_analysis",
    factory=DataAnalysisFactory()
)

# 构造任务（指定使用DeepSeek模型）
task = Task(
    type="data_analysis",  # 对应代理工厂类型
    parameters={
        "data_engine_config": {"api_key": "finnhub_key"},  # DataEngine配置
        "model_config": {
            "model": "deepseek-llm-7b",  # DeepSeek模型特有的配置
            "temperature": 0.5
        }
    },
    model_type="deepseek"  # 指定使用DeepSeek网关
)

# 执行任务
result = engine.execute_task(task)
print("数据分析结果（DeepSeek生成）:", result)