#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: quantitative_strategies.py
Created Time: 2025-07-10 15:32:40
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""


from typing import Any, Dict
from myfinrobot.functional.quantitative import BackTraderUtils
from ..strategy_factory.strategy_interface import IQuantitativeStrategy


class SMACrossoverStrategy(IQuantitativeStrategy):
    """SMA均线交叉策略"""
    def backtest(self, **kwargs) -> Dict[str, Any]:
        return BackTraderUtils.backtest(
            symbol=kwargs['symbol'],
            start_date=kwargs['start_date'],
            end_date=kwargs['end_date'],
            strategy='sma_crossover',
            fast_period=kwargs.get('fast_period', 20),
            slow_period=kwargs.get('slow_period', 50)
        )

class MeanReversionStrategy(IQuantitativeStrategy):
    """均值回归策略"""
    def backtest(self, **kwargs) -> Dict[str, Any]:
        return BackTraderUtils.backtest(
            symbol=kwargs['symbol'],
            start_date=kwargs['start_date'],
            end_date=kwargs['end_date'],
            strategy='mean_reversion',
            lookback_period=kwargs.get('lookback_period', 30),
            z_threshold=kwargs.get('z_threshold', 2.0)
        )