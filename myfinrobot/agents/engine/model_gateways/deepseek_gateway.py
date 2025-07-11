#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: deepseek_gateway.py
Created Time: 2025-07-15 14:30:00
Author: Coin Lau (jinxinliu@gmail.com)
Description: DeepSeek大模型网关实现，支持调用DeepSeek智能模型生成内容
"""
import requests
from typing import Dict, Any

from myfinrobot.debugprinter import DebugPrinter
from ..agent_engine import ModelGateway  # 从engine模块导入抽象接口

from openai import OpenAI

class DeepSeekGateway(ModelGateway):
    def __init__(self, api_key: str, api_base: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek模型网关
        
        Args:
            api_key: DeepSeek API Key（必填）
            api_base: API接口地址（默认使用官方地址）
        """
        self.api_key = api_key
        self.base_url = api_base
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        """
        调用DeepSeek模型生成内容
        
        Args:
            prompt: 输入提示词
            config: 模型配置（支持model/temperature/max_tokens等参数）
            
        Returns:
            模型生成的文本内容
            
        Raises:
            ValueError: API调用失败时抛出
        """
        # 构造请求参数（兼容DeepSeek API格式）
        payload = {
            "model": config.get("model", "deepseek-chat"),  # 默认使用7B模型
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2048)
        }
        DebugPrinter().debug_print(
            'DeepSeekGateway generate payload:',
            payload
        )

        DebugPrinter().debug_print(
            'Calling DeepSeek API with parameters:',
            self.api_key, "API Base URL:",
            self.base_url)

                # 调用API
        # response = requests.post(
        #     url=self.api_base,
        #     headers=self.headers,
        #     json=payload,
        #     timeout=config.get("timeout", 30)
        # )
        response = self.client.chat.completions.create(
            model=payload["model"],
            messages=payload["messages"],
            temperature=payload["temperature"],
            max_tokens=payload["max_tokens"]
        )
        DebugPrinter().debug_print(
            'DeepSeek API response content:',
            response
        )
        # 处理响应
        if response.choices is None:
            raise ValueError(
                f"DeepSeek API调用失败（状态码：{response.status_code}）: "
                f"{response.json().get('error', {}).get('message', '未知错误')}"
            )
        content = response.choices[0].message.content
        DebugPrinter().debug_print(
            'DeepSeek API response content:',
            content
        )
        return content
    