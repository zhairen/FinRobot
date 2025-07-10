#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: finnhub_source.py
Created Time: 2025-07-10 13:23:40
Author: Coin Lau (jinxinliu@gmail.com)
Description: finnhub数据源实现  
implementing IDataSource interface for fetching stock data
datasource is finnhub
"""

import os
from typing import Dict, List
from .interfaces import IDataSourceFactory, IStockDataSource, IFundamentalDataSource
from ..data_source.finnhub_utils import FinnHubUtils
import pandas as pd

class FinnhubFundamentalSource(IFundamentalDataSource):    
    def get_company_news(self, symbol: str, **kwargs) -> pd.DataFrame:
        return FinnHubUtils.get_company_news(symbol=symbol, **kwargs)

class FinnhubFactory(IDataSourceFactory):
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(project_root, 'config_api_keys')
        from myfinrobot.utils import register_keys_from_json
        register_keys_from_json(config_path)
        
    def create_stock_source(self) -> IStockDataSource:
        raise NotImplementedError("暂未实现Finnhub股票数据")

    def create_fundamental_source(self) -> IFundamentalDataSource:
        return FinnhubFundamentalSource()