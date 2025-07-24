#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: analysis_strategies.py
Created Time: 2025-07-10 15:32:14
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

from ..functional.analyzer import ReportAnalysisUtils
from .strategy_interface import IAnalysisStrategy

class IncomeAnalysisStrategy(IAnalysisStrategy):
    """收益表分析策略"""
    def execute(self, **kwargs) -> str:
        return ReportAnalysisUtils.analyze_income_stmt(
            ticker_symbol=kwargs['ticker_symbol'],
            fyear=kwargs['fyear'],
            save_path=kwargs['save_path']
        )

class BalanceSheetAnalysisStrategy(IAnalysisStrategy):
    """资产负债表分析策略"""
    def execute(self, **kwargs) -> str:
        return ReportAnalysisUtils.analyze_balance_sheet(
            symbol=kwargs['ticker_symbol'],
            fyear=kwargs['fyear'],
            save_path=kwargs['save_path']
        )

class RiskAssessmentStrategy(IAnalysisStrategy):
    """风险评估策略"""
    def execute(self, **kwargs) -> str:
        return ReportAnalysisUtils.get_risk_assessment(
            ticker_symbol=kwargs['ticker_symbol'],
            fyear=kwargs['fyear'],
            save_path=kwargs['save_path']
        )