#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: anthropic.py
Created Time: 2025-07-10 23:21:40
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from typing import Dict, Any
from ..agent_engine import ModelGateway  # 假设已定义ModelGateway基类
import anthropic

class AnthropicGateway(ModelGateway):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        response = self.client.completions.create(
            model=config.get("model", "claude-2"),
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            max_tokens_to_sample=config.get("max_tokens", 1500),
            temperature=config.get("temperature", 0.7),
        )
        return response.completion