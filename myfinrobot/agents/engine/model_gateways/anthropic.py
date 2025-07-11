#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: anthropic.py
Created Time: 2025-07-10 23:21:40
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
from ..model_gateways import ModelGateway
import anthropic

class AnthropicGateway(ModelGateway):
    def generate(self, prompt: str, config: Dict[str, Any]) -> str:
        client = anthropic.Client(api_key=config["api_key"])
        response = client.completion(
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            model=config.get("model", "claude-2"),
            max_tokens_to_sample=config.get("max_tokens", 1000),
            temperature=config.get("temperature", 0.5),
        )
        return response["completion"]