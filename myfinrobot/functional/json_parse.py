#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: json_parse.py
Created Time: 2025-07-17 21:41:34
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
"""
This module provides a function to parse JSON strings that may have missing closing quotes or braces.
It attempts to correct these issues and returns a valid JSON string or the original string if it cannot"""
def parse_relaxed_json(json_str: str) -> str:
    # 补全缺失的右引号
    quote_count = json_str.count('"')
    if quote_count % 2 != 0:
        json_str += '"'
    
    # 补全缺失的右大括号
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    json_str += '}' * (open_braces - close_braces)
    
    # 简单验证
    try:
        import json
        json.loads(json_str)
    except:
        # 如果仍然无效则返回对象
        return json_str   
    return json_str