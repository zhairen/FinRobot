#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: data_engine.py
Created Time: 2025-07-09 19:59:18
Author: Coin Lau (jinxinliu@gmail.com)
Description:  data engine for fetching stock data
"""

import pandas as pd
from typing import Dict, Any
from cachetools import TTLCache

from myfinrobot.data_factory.source_factory import DataSourceFactory

class DataEngine:
    """智能数据引擎"""
    def __init__(self, cache_enabled=True):
        self.cache = TTLCache(maxsize=1000, ttl=3600) if cache_enabled else None
    
    def get_historical_data(self, symbol: str, **kwargs) -> pd.DataFrame:
        """智能获取历史数据"""
        source = DataSourceFactory.get_strategy_source('historical').create_stock_source()
        cache_key = f"hist_{symbol}_{kwargs}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        data = source.get_historical_data(symbol, **kwargs)
        if self.cache:
            self.cache[cache_key] = data
        return data
    
    def get_company_news(self, symbol: str, **kwargs) -> pd.DataFrame:
        """智能获取公司新闻数据"""
        source = DataSourceFactory.get_strategy_source('fundamental').create_fundamental_source()
        return source.get_company_news(symbol, **kwargs)

    def set_data_strategy(self, data_type: str, source_name: str):
        """运行时动态调整策略"""
        DataSourceFactory.set_strategy_rule(data_type, source_name)