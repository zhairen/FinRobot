#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇数据源接口与真实API实现（AlphaVantage/OANDA）"""
import pandas as pd
import requests
from typing import Dict, Any
from datetime import datetime
from cachetools import TTLCache
from myfinrobot.data_factory.interfaces import IExtendedDataSource

class IForexDataSource(IExtendedDataSource):
    """外汇数据源核心接口"""
    def get_historical_data(
        self, symbol: str, timeframe: str = "D", **kwargs
    ) -> pd.DataFrame:
        """获取历史汇率数据（symbol格式如EUR/USD）"""
        raise NotImplementedError

    def get_economic_events(
        self, currency: str, **kwargs
    ) -> pd.DataFrame:
        """获取宏观经济事件数据（如利率决议）"""
        raise NotImplementedError

class AlphaVantageForexSource(IForexDataSource):
    _BASE_URL = "https://www.alphavantage.co/query"
    _CACHE = TTLCache(maxsize=1000, ttl=3600)  # 1小时缓存

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_historical_data(self, symbol: str, timeframe: str = "D", **kwargs) -> pd.DataFrame:
        cache_key = f"alpha_hist_{symbol}_{timeframe}"
        if cache_key in self._CACHE:
            return self._CACHE[cache_key]

        params = {
            "function": "FX_DAILY" if timeframe == "D" else "FX_INTRADAY",
            "from_symbol": symbol.split("/")[0],
            "to_symbol": symbol.split("/")[1],
            "interval": timeframe if timeframe != "D" else "daily",
            "apikey": self.api_key
        }
        try:
            response = requests.get(self._BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time_series = data.get(f"Time Series FX ({timeframe})", {})
            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = ["open", "high", "low", "close"]
            df = df.astype(float)
            self._CACHE[cache_key] = df
            return df
        except Exception as e:
            raise ValueError(f"AlphaVantage历史数据获取失败：{str(e)}")

    def get_economic_events(self, currency: str, **kwargs) -> pd.DataFrame:
        # 简化实现，实际需调用AlphaVantage经济日历API
        return pd.DataFrame({
            "event": ["Interest Rate Decision", "CPI"],
            "date": [datetime(2024, 1, 31), datetime(2024, 2, 15)],
            "impact": ["High", "Medium"]
        })

class OANDAForexSource(IForexDataSource):
    _BASE_URL = "https://api-fxpractice.oanda.com/v3"
    _CACHE = TTLCache(maxsize=1000, ttl=3600)  # 1小时缓存

    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_historical_data(self, symbol: str, timeframe: str = "D", **kwargs) -> pd.DataFrame:
        cache_key = f"oanda_hist_{symbol}_{timeframe}"
        if cache_key in self._CACHE:
            return self._CACHE[cache_key]

        params = {
            "granularity": timeframe,
            "count": kwargs.get("count", 1000)
        }
        try:
            response = requests.get(
                f"{self._BASE_URL}/instruments/{symbol}/candles",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            candles = data.get("candles", [])
            df = pd.DataFrame([{
                "time": candle["time"],
                "open": float(candle["mid"]["o"]),
                "high": float(candle["mid"]["h"]),
                "low": float(candle["mid"]["l"]),
                "close": float(candle["mid"]["c"])
            } for candle in candles])
            df["time"] = pd.to_datetime(df["time"])
            self._CACHE[cache_key] = df
            return df
        except Exception as e:
            raise ValueError(f"OANDA历史数据获取失败：{str(e)}")

    def get_economic_events(self, currency: str, **kwargs) -> pd.DataFrame:
        # 简化实现，实际需调用OANDA市场新闻API
        return pd.DataFrame({
            "event": ["ECB Meeting", "Non-Farm Payrolls"],
            "date": [datetime(2024, 3, 15), datetime(2024, 4, 5)],
            "impact": ["High", "Very High"]
        })

class ForexDataSourceFactory:
    """外汇数据源工厂（支持运行时切换）"""
    @staticmethod
    def create_source(source_type: str, config: Dict[str, Any]) -> IForexDataSource:
        if source_type == "alpha_vantage":
            return AlphaVantageForexSource(api_key=config["api_key"])
        elif source_type == "oanda":
            return OANDAForexSource(
                access_token=config["access_token"],
                account_id=config["account_id"]
            )
        else:
            raise ValueError(f"不支持的数据源类型：{source_type}")