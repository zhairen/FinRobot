#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: agent_engine.py
Created Time: 2025-07-10 23:19:19
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

class Task:
    def __init__(self, task_type: str, parameters: Dict[str, Any], model_type: str):
        self.type = task_type
        self.parameters = parameters
        self.model_type = model_type

class ModelGateway(ABC):
    @abstractmethod
    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        pass

class Agent(ABC):
    @abstractmethod
    def execute(self, task: Task, gateway: ModelGateway) -> Any:
        pass

class AgentFactory(ABC):
    @abstractmethod
    def create_agent(self, config: Dict[str, Any]) -> Agent:
        pass

class AgentEngine:
    def __init__(self):
        self.model_gateways = {}
        self.agent_factories = {}

    def register_model(self, name: str, gateway: ModelGateway):
        self.model_gateways[name] = gateway

    def register_agent_factory(self, agent_type: str, factory: AgentFactory):
        self.agent_factories[agent_type] = factory

    def execute_task(self, task: Task) -> Any:
        # 获取模型网关
        gateway = self.model_gateways.get(task.model_type)
        if not gateway:
            raise ValueError(f"Model gateway not found: {task.model_type}")
        
        # 获取代理工厂
        factory = self.agent_factories.get(task.type)
        if not factory:
            raise ValueError(f"Agent factory not found for task type: {task.type}")
        
        # 创建代理并执行任务
        agent = factory.create_agent(task.parameters)
        return agent.execute(task, gateway)