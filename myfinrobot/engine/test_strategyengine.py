#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_strategyengine.py
Created Time: 2025-07-10 15:40:03
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

# 在应用初始化时注册策略
from myfinrobot.engine.strategy_engine import StrategyEngine
import pandas as pd

def main():
    # 使用分析策略        
    # 初始化策略引擎
    strategy_engine = StrategyEngine()
    
    result = strategy_engine.execute_analysis(
    strategy_name='income',
    ticker_symbol='NVDA',
    fyear='2025',
    save_path='./analysis/income_nvda.txt')

    df = pd.read_table('./analysis/income_nvda.txt')
    print(df)

    pass

if __name__ == "__main__":
    main()
