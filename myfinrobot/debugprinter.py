#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: debupPrinter.py
Created Time: 2025-07-11 19:52:29
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

class DebugPrinter:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.is_debug = True  # 默认开启调试模式
        return cls._instance
    
    def debug_print(self, *args, **kwargs):
        if self.is_debug:
            print("[DEBUG]", *args, **kwargs)