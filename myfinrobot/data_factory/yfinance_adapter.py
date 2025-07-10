#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: yfinance_source.py
Created Time: 2025-07-10 13:22:49
Author: Coin Lau (jinxinliu@gmail.com)
Description: yfinance数据源实现  策略模式 + 桥接模式 + 工厂方法
"""

import pandas as pd
from .interfaces import IDataSourceFactory, IFundamentalDataSource, IStockDataSource
from ..data_source.yfinance_utils import YFinanceUtils

class YFinanceStockSource(IStockDataSource):
    def get_historical_data(self, symbol: str, **kwargs) -> pd.DataFrame:
        return YFinanceUtils.get_stock_data(symbol, **kwargs)
    
    def get_current_price(self, symbol: str) -> float:
        return YFinanceUtils.get_current_price(symbol)

class YFinanceFactory(IDataSourceFactory):
    def create_stock_source(self) -> IStockDataSource:
        return YFinanceStockSource()
    
    def create_fundamental_source(self) -> IFundamentalDataSource:
        raise NotImplementedError("YFinance不支持基本面数据")
