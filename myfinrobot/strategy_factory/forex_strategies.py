#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇策略完整实现（含错误处理）"""
import pandas as pd
from typing import Dict, Any
from ..strategy_factory.strategy_interface import (
    IAnalysisStrategy,
    IQuantitativeStrategy  # 复用现有策略接口
)
from ..utils.logger import logger  # 复用项目日志工具

class ForexFundamentalAnalysis(IAnalysisStrategy):
    """外汇基本面分析（利率差异+经济指标）"""
    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            economic_events = kwargs["economic_events"]
            # 计算利率差异（示例）
            interest_rates = economic_events[economic_events["event"] == "Interest Rate Decision"]
            if interest_rates.empty:
                raise ValueError("未找到利率决议数据")
            latest_rate = interest_rates.sort_values("date").iloc[-1]
            return {
                "analysis_type": "fundamental",
                "key_metrics": {
                    "latest_interest_rate": latest_rate["rate"],
                    "next_meeting_date": latest_rate["date"]
                },
                "conclusion": f"{kwargs['symbol']}当前利率为{latest_rate['rate']}%，下次会议日期：{latest_rate['date']}"
            }
        except Exception as e:
            logger.error(f"基本面分析失败：{str(e)}")
            raise

class ForexRSIStrategy(IQuantitativeStrategy):
    """外汇RSI技术指标策略（完整计算逻辑）"""
    def backtest(self, **kwargs) -> Dict[str, Any]:
        try:
            historical_data = kwargs["historical_data"]
            if "close" not in historical_data.columns:
                raise ValueError("历史数据缺少'close'列")
            
            # 计算RSI（标准14周期）
            delta = historical_data["close"].diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14, min_periods=14).mean()
            avg_loss = loss.rolling(window=14, min_periods=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # 生成信号
            signals = []
            for rsi_val in rsi:
                if rsi_val < 30:
                    signals.append("BUY")
                elif rsi_val > 70:
                    signals.append("SELL")
                else:
                    signals.append("HOLD")
            
            return {
                "strategy_type": "rsi",
                "last_rsi": rsi.iloc[-1],
                "last_signal": signals[-1]
            }
        except Exception as e:
            logger.error(f"RSI策略执行失败：{str(e)}")
            raise

class CarryTradeArbitrage(IQuantitativeStrategy):
    """套息交易套利策略（多货币对支持）"""
    def backtest(self, **kwargs) -> Dict[str, Any]:
        try:
            interest_rates = kwargs["interest_rates"]  # 格式：{"USD": 5.25, "JPY": 0.1}
            base, quote = kwargs["symbol"].split("/")
            if base not in interest_rates or quote not in interest_rates:
                raise ValueError(f"缺少{base}/{quote}的利率数据")
            
            carry_return = interest_rates[base] - interest_rates[quote]
            return {
                "strategy_type": "carry_trade",
                "carry_return": f"{carry_return:.2f}%",
                "recommendation": "适合长期持有" if carry_return > 0 else "不建议持有"
            }
        except Exception as e:
            logger.error(f"套利策略执行失败：{str(e)}")
            raise