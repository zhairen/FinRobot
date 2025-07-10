#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: strategy_engine.py
Created Time: 2025-07-10 15:38:31
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""


from typing import Dict, Any
from ..strategy_factory.invstrategy_factory import InvStrategyFactory
from ..strategy_factory.strategy_interface import IAnalysisStrategy, IQuantitativeStrategy
import os

class StrategyEngine:
    """策略引擎（门面模式）"""
    def __init__(self):
        # 注册默认策略
        self._register_default_strategies()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(project_root, 'config_api_keys')
        from myfinrobot.utils import register_keys_from_json
        print(config_path)
        register_keys_from_json(config_path)
    
    def _register_default_strategies(self):
        """注册默认策略"""
        from ..strategy_factory.analysis_strategies import (
            IncomeAnalysisStrategy,
            BalanceSheetAnalysisStrategy,
            RiskAssessmentStrategy
        )
        from ..strategy_factory.quantitative_strategies import (
            SMACrossoverStrategy,
            MeanReversionStrategy
        )
        
        # 注册分析策略
        InvStrategyFactory.register_analysis_strategy('income', IncomeAnalysisStrategy)
        InvStrategyFactory.register_analysis_strategy('balance', BalanceSheetAnalysisStrategy)
        InvStrategyFactory.register_analysis_strategy('risk', RiskAssessmentStrategy)

        # 注册量化策略
        InvStrategyFactory.register_quantitative_strategy('sma_crossover', SMACrossoverStrategy)
        InvStrategyFactory.register_quantitative_strategy('mean_reversion', MeanReversionStrategy)
    
    def execute_analysis(self, strategy_name: str, **kwargs) -> Any:
        """执行分析策略"""
        strategy = InvStrategyFactory.create_analysis_strategy(strategy_name)
        return strategy.execute(**kwargs)
    
    def execute_quantitative(self, strategy_name: str, **kwargs) -> Dict[str, Any]:
        """执行量化策略"""
        strategy = InvStrategyFactory.create_quantitative_strategy(strategy_name)
        return strategy.backtest(**kwargs)
    
    def register_custom_strategy(self, strategy_type: str, name: str, strategy_class):
        """注册自定义策略"""
        if strategy_type == 'analysis':
            InvStrategyFactory.register_analysis_strategy(name, strategy_class)
        elif strategy_type == 'quantitative':
            InvStrategyFactory.register_quantitative_strategy(name, strategy_class)
        else:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")