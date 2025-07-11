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
from ..agent_engine import ModelGateway  # 从engine模块导入抽象接口

class DeepSeekGateway(ModelGateway):
    def __init__(self, api_key: str, api_base: str = "https://api.deepseek.com/v1/chat/completions"):
        """
        初始化DeepSeek模型网关
        
        Args:
            api_key: DeepSeek API Key（必填）
            api_base: API接口地址（默认使用官方地址）
        """
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
            "model": config.get("model", "deepseek-llm-7b"),  # 默认使用7B模型
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2048)
        }

        # 调用API
        response = requests.post(
            url=self.api_base,
            headers=self.headers,
            json=payload,
            timeout=config.get("timeout", 30)
        )

        # 处理响应
        if response.status_code != 200:
            raise ValueError(
                f"DeepSeek API调用失败（状态码：{response.status_code}）: "
                f"{response.json().get('error', {}).get('message', '未知错误')}"
            )
        
        # 提取生成内容（根据DeepSeek返回结构调整）
        return response.json()["choices"][0]["message"]["content"]