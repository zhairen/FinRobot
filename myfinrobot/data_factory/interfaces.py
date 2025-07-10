#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: interfaces.py
Created Time: 2025-07-10 13:21:59
Author: Coin Lau (jinxinliu@gmail.com)
Description:  interfaces for data factory
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class IStockDataSource(ABC):
    """股票数据源标准接口"""
    @abstractmethod
    def get_historical_data(self, symbol: str, **kwargs) -> pd.DataFrame: ...
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float: ...

class IFundamentalDataSource(ABC):
    """基本面数据接口"""
    @abstractmethod
    def get_company_news(self, symbol: str, **kwargs) -> pd.DataFrame: ...

class IDataSourceFactory(ABC):
    """抽象工厂接口"""
    @abstractmethod
    def create_stock_source(self) -> IStockDataSource: ...
    
    @abstractmethod
    def create_fundamental_source(self) -> IFundamentalDataSource: ...