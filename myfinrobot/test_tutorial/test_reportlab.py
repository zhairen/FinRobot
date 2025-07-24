#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_reportlab.py
Created Time: 2025-07-17 20:57:28
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""

import json
from myfinrobot.functional.reportlab import parse_relaxed_json

def test_quote_repair():
    # 用例1：修复缺失右引号
    input = '{"key": "value'  
    output = parse_relaxed_json(input)
    print('output ',output)
    assert json.loads(output) == {"key": "value"}


# 在文件末尾添加
if __name__ == "__main__":
    def run_manual_tests():
        tests = [
            test_quote_repair
        ]
        
        passed = 0
        failed = 0
        for test in tests:
            try:
                test()
                print(f"✅ {test.__name__} 通过")
                passed += 1
            except AssertionError as e:
                print(f"❌ {test.__name__} 失败: {str(e)}")
                failed += 1
        
        print(f"\n测试结果：{passed} 通过，{failed} 失败")

    run_manual_tests()