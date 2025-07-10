#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: strategy_interface.py
Created Time: 2025-07-10 15:25:52
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""


from abc import ABC, abstractmethod
from typing import Dict, Any

class IAnalysisStrategy(ABC):
    """分析策略统一接口"""
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行分析策略"""
        pass

class IQuantitativeStrategy(ABC):
    """量化策略统一接口"""
    @abstractmethod
    def backtest(self, **kwargs) -> Dict[str, Any]:
        """执行回测策略"""
        pass