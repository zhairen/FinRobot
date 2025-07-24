#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: agent_engine.py
Created Time: 2025-07-10 23:19:19
Author: Coin Lau (jinxinliu@gmail.com)
Description: 智能体引擎核心实现，负责管理模型网关、代理工厂及任务执行，支持DataEngine/StrategyEngine依赖注入
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

# 初始化基础日志配置（新增）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Task:
    # 参数名修正为与类图一致（原task_type改为type）
    def __init__(self, type: str, parameters: Dict[str, Any], model_type: str):
        """
        任务描述类
        
        Args:
            type: 任务类型（对应代理工厂类型，如"data_analysis"）
            parameters: 任务参数（包含DataEngine/StrategyEngine等依赖的配置）
            model_type: 使用的大模型类型（对应注册的模型网关名称）
        """
        self.type = type
        self.parameters = parameters
        self.model_type = model_type

class ModelGateway(ABC):
    """模型网关抽象接口，定义大模型调用规范（支持OpenAI/Anthropic等）"""
    
    @abstractmethod
    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        """
        调用大模型生成内容
        
        Args:
            prompt: 输入提示词（由具体代理生成）
            config: 模型配置（如temperature、max_tokens等）
            
        Returns:
            模型生成的文本内容
        """
        pass

class Agent(ABC):
    """智能体抽象接口，定义任务执行规范"""
    
    @abstractmethod
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        """
        执行具体任务（由具体代理实现）
        
        Args:
            task: 待执行的任务描述（包含参数和模型类型）
            gateway: 用于生成内容的模型网关实例
            
        Returns:
            任务执行结果（具体类型由代理决定）
        """
        pass

class AgentFactory(ABC):
    """代理工厂抽象接口，定义代理创建规范"""
    
    @abstractmethod
    def create_agent(self, config: Dict[str, Any]) -> Agent:
        """
        创建具体代理实例（支持从agent_library加载预配置）
        
        Args:
            config: 代理配置参数（包含依赖引擎的初始化配置）
            
        Returns:
            Agent 实例
        """
        pass

logger = logging.getLogger(__name__)

class AgentEngine:
    def __init__(self):
        self.model_gateways: Dict[str, ModelGateway] = {}  # 模型网关注册表（key: 模型类型）
        self.agent_factories: Dict[str, AgentFactory] = {}  # 代理工厂注册表（key: 任务类型）

    def register_model(self, name: str, gateway: ModelGateway):
        """
        注册模型网关（支持OpenAI/Anthropic等）
        
        Args:
            name: 模型类型名称（如"openai"/"anthropic"）
            gateway: 模型网关实例
        """
        if name in self.model_gateways:
            logger.warning(f"模型网关[{name}]已存在，将覆盖原有实例")
        self.model_gateways[name] = gateway
        logger.info(f"成功注册模型网关：{name}（当前注册数：{len(self.model_gateways)}）")

    def register_agent_factory(self, agent_type: str, factory: AgentFactory):
        """
        注册代理工厂（支持数据分析/交易策略等）
        
        Args:
            agent_type: 代理类型（对应任务类型，如"data_analysis"）
            factory: 代理工厂实例
        """
        if agent_type in self.agent_factories:
            logger.warning(f"代理工厂[{agent_type}]已存在，将覆盖原有实例")
        self.agent_factories[agent_type] = factory
        logger.info(f"成功注册代理工厂：{agent_type}（当前注册数：{len(self.agent_factories)}）")

    def execute_task(self, task: Task) -> Any:
        """
        执行具体任务的核心流程
        
        Args:
            task: 待执行的任务描述
            
        Returns:
            任务执行结果
            
        Raises:
            ValueError: 模型网关或代理工厂未找到时抛出
        """
        try:
            # 1. 校验并获取模型网关
            gateway = self.model_gateways.get(task.model_type)
            if not gateway:
                raise ValueError(
                    f"模型网关[{task.model_type}]未找到，"
                    f"当前已注册网关：{list(self.model_gateways.keys())}"
                )
            logger.debug(f"获取模型网关成功：{task.model_type}")

            # 2. 校验并获取代理工厂
            factory = self.agent_factories.get(task.type)
            if not factory:
                raise ValueError(
                    f"代理工厂[{task.type}]未找到，"
                    f"当前已注册工厂：{list(self.agent_factories.keys())}"
                )
            logger.debug(f"获取代理工厂成功：{task.type}")

            # 3. 创建代理实例（添加类型校验）
            agent = factory.create_agent(task.parameters)
            if not isinstance(agent, Agent):
                raise TypeError(
                    f"工厂[{factory.__class__.__name__}]返回无效类型，"
                    f"期望Agent实例，实际得到{type(agent)}"
                )
            logger.info(f"成功创建代理实例：{agent.__class__.__name__}")

            # 4. 执行任务（优化结果日志）
            logger.info(f"开始执行任务：类型={task.type}, 参数={task.parameters}")
            result = agent.execute(task, gateway)
            
            # 安全处理结果日志（非字符串类型显示类型）
            result_log = result[:50] if isinstance(result, str) else f"<{type(result).__name__}>类型结果"
            logger.info(f"任务执行完成，结果={result_log}...（截断）")

            return result
        except Exception as e:
            logger.error(f"任务[{task.type}]执行失败（参数：{task.parameters}）：{str(e)}", exc_info=True)
            raise  # 保持异常向上传递