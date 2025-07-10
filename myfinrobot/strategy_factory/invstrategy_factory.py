#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: invstrategy_factory.py
Created Time: 2025-07-10 15:31:37
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

from typing import Dict, Type
from .strategy_interface import IAnalysisStrategy, IQuantitativeStrategy
import os

class InvStrategyFactory:
    """策略工厂（注册和创建策略实例）"""
    
    _analysis_strategies: Dict[str, Type[IAnalysisStrategy]] = {}
    _quantitative_strategies: Dict[str, Type[IQuantitativeStrategy]] = {}
    
    @classmethod
    def register_analysis_strategy(cls, name: str, strategy_class: Type[IAnalysisStrategy]):
        """注册分析策略"""
        cls._analysis_strategies[name] = strategy_class
        
    @classmethod
    def register_quantitative_strategy(cls, name: str, strategy_class: Type[IQuantitativeStrategy]):
        """注册量化策略"""
        cls._quantitative_strategies[name] = strategy_class
        
    @classmethod
    def create_analysis_strategy(cls, name: str) -> IAnalysisStrategy:
        """创建分析策略实例"""
        return cls._analysis_strategies[name]()
    
    @classmethod
    def create_quantitative_strategy(cls, name: str) -> IQuantitativeStrategy:
        """创建量化策略实例"""
        return cls._quantitative_strategies[name]()