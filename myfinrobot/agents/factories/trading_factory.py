#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: trading_factory.py
Created Time: 2025-07-10 23:23:05
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ...agents.trading_agent import TradingStrategyAgent
from ..engine import AgentFactory

class TradingStrategyFactory(AgentFactory):
    def create_agent(self, config: Dict[str, Any]) -> TradingStrategyAgent:
        return TradingStrategyAgent(config)