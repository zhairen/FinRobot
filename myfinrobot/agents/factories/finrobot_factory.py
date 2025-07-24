#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: finrobot_factory.py
Created Time: 2025-07-10 23:23:31
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from typing import Any, Dict
from ..agents.finrobot_adapter import FinRobotAdapter
from ..engine.agent_engine import AgentFactory

class FinRobotFactory(AgentFactory):
    def create_agent(self, config: Dict[str, Any]) -> FinRobotAdapter:
        return FinRobotAdapter(config)