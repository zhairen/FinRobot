#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: testengine.py
Created Time: 2025-07-09 20:24:20
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

from myfinrobot.engine.data_engine import DataEngine


def main():
    engine = DataEngine()

    # 自动按策略选择数据源
    history = engine.get_historical_data("AAPL",start_date= "2025-07-01",end_date= "2025-07-31")  # 使用yfinance
    print(history)
    news = engine.get_company_news("MSFT",start_date= "2025-07-01",end_date= "2025-07-31")  # 使用finnhub
    print(news)
    # 动态切换策略
    engine.set_data_strategy('historical', 'finnhub')  # 历史数据改为finnhub
    print("change datasource to finnhub")
    pass

if __name__ == "__main__":
    main()
