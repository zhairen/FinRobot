#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: source_factory.py
Created Time: 2025-07-10 13:24:36
Author: Coin Lau (jinxinliu@gmail.com)
Description: factory for creating data source instances
"""
# myfinrobot/data_source/source_manager.py
from typing import Dict, Type

from myfinrobot.data_factory.finnhub_adapter import FinnhubFactory
from myfinrobot.data_factory.yfinance_adapter import YFinanceFactory
from .interfaces import IDataSourceFactory

class DataSourceFactory:
    """数据源注册与策略管理中心"""
    _factories: Dict[str, Type[IDataSourceFactory]] = {}
    _strategy_rules = {
        'historical': 'yfinance',
        'realtime': 'finnhub',
        'fundamental': 'finnhub'
    }
    
    @classmethod
    def register_factory(cls, name: str, factory_class: Type[IDataSourceFactory]):
        """注册新数据源工厂"""
        cls._factories[name] = factory_class
    
    @classmethod
    def get_factory(cls, name: str, **kwargs) -> IDataSourceFactory:
        """获取数据源工厂实例"""
        return cls._factories[name](**kwargs)
    
    @classmethod
    def set_strategy_rule(cls, data_type: str, source_name: str):
        """动态修改策略规则"""
        cls._strategy_rules[data_type] = source_name
    
    @classmethod
    def get_strategy_source(cls, data_type: str, **kwargs) -> IDataSourceFactory:
        """根据策略获取数据源"""
        return cls.get_factory(cls._strategy_rules[data_type], **kwargs)

# 注册默认数据源
DataSourceFactory.register_factory('yfinance', YFinanceFactory)
DataSourceFactory.register_factory('finnhub', FinnhubFactory)