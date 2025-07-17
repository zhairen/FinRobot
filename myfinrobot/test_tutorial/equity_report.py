#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: EquityReport.py
Created Time: 2025-07-17 10:02:50
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
Take a company's 10-k form, financial data, 
and market data as input and output
an equity research report
"""

import os
import autogen
from textwrap import dedent
from myfinrobot.utils import register_keys_from_json
from myfinrobot.agents.workflow import SingleAssistantShadow

def main():

    llm_config = {
            "config_list": [{
                "model": "qwen-plus",
                "api_key": "sk-33e77da7a560490cbc6e053c91e2e6a0",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",  # DeepSeek API 端点  
                "max_tokens": 1000,
                "price": [0.0, 0.0]           
            }],
            "timeout": 600
        }
    # Register FINNHUB API keys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(project_root, 'config_api_keys')

    from myfinrobot.utils import register_keys_from_json

    register_keys_from_json("config_api_keys")

    # Intermediate strategy modules will be saved in this directory
    work_dir = "./testreport"
    os.makedirs(work_dir, exist_ok=True)

    assistant = SingleAssistantShadow(
        "Expert_Investor",
        llm_config,
        max_consecutive_auto_reply=None,
        human_input_mode="TERMINATE",
    )

    company = "AAPL"  
    fyear = "2025"

    message = dedent(
        f"""
        使用你已获得的工具，基于{company}的{ fyear }年10-K报告撰写一份年度报告，并将其格式化为PDF文件。
        请注意以下事项：
        - 所有内容（包括工具返回的原始数据、分析结论、表格标题等）必须完整翻译成中文。        
        - 生成的HTML报告需包含以下完整结构（确保中文字体和编码生效）：
          <!DOCTYPE html>
          <html>
          <head>
              <meta charset="utf-8">  <!-- 强制UTF-8编码 -->
              <title>{company}年度报告</title>
              <style>
                  body {{ 
                      font-family: 'Noto Sans CJK SC', 'SimSun', sans-serif;  /* 双保险指定中文字体 */
                      font-size: 14px; 
                      line-height: 1.6; 
                  }}
              </style>
          </head>
          <body>
              <!-- 报告内容 -->
          </body>
          </html>
        - 开始前需用中文明确说明你的工作方案（例如：先调用get_sec_report获取10-K报告链接→提取关键财务数据→分析核心指标→翻译所有英文内容→生成中文报告）。
        - 为保证清晰，需逐个使用工具（尤其是在请求指令时）。
        - 所有文件操作需在目录"{work_dir}"中完成。
        - 生成的任何图片需在对话中展示。
        - 所有段落总字数大约在300-500字之间，但不超过1700字。        
        - 若工具返回英文数据（如10-K报告中的财务指标、段落描述），需先完整翻译成中文后再用于报告撰写。
        - 生成PDF时需使用pdfkit库，调用pdfkit.from_string(html_template, pdf_path)生成PDF。 。
    """
    )

    assistant.chat(message, use_cache=True, max_turns=50,
                summary_method="last_msg")
    #fmp key1 BMVM2VVKROi7vjFnfBgQXC58C4bqMgF2
    #fmp key2 no056gp10mlfxJCOcIHCpjGuNgDD0KUp
    #fmp key3 0Eqyot3JziBs2Lfge2suyWOQWo3WyX7p
    
    pass

if __name__ == "__main__":
    main()
