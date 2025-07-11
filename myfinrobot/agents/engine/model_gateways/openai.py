#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: openai.py
Created Time: 2025-07-10 23:21:09
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ..model_gateways import ModelGateway
import openai

class OpenAIGateway(ModelGateway):
    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        response = openai.ChatCompletion.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 1500),
        )
        return response.choices[0].message.content
    