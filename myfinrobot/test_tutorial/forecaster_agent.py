#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: forecasteragent.py
Created Time: 2025-07-16 13:44:13
Author: Coin Lau (jinxinliu@gmail.com)
Description: 
"""
import warnings

from myfinrobot.debugprinter import DebugPrinter
warnings.filterwarnings("ignore", message="Field \"model_client_cls\" in LLMConfigEntry has conflict with protected namespace \"model_\".")

import autogen
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant
import pdfkit  # 新增：导入pdfkit库

def main():
    # Read OpenAI API keys from a JSON file
    # llm_config = {
    #     "config_list": autogen.config_list_from_json(
    #         "../OAI_CONFIG_LIST",
    #         filter_dict={"model": ["gpt-4-0125-preview"]},
    #     ),
    #     "timeout": 120,
    #     "temperature": 0,
    # }
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


    company = "NVDA"  # 设置公司名称

    # 修正拼写错误：assitant → assistant
    assistant = SingleAssistant(
        "Market_Analyst",
        llm_config,
        # set to "ALWAYS" if you want to chat instead of simply receiving the prediciton
        human_input_mode="NEVER",
    )
    assistant.chat(  # 同步修正此处变量名
         f"请用中文回答，使用所有提供的工具，检索截至{get_current_date()}的{company}相关信息。分析{company}的积极进展与潜在问题（各选取2-4个最重要因素，保持简洁，大部分因素应从公司相关新闻中推断）。"
         f"说明{company}今年以来和本月股票价格涨跌幅，最新收盘价,并提供PE PB数据。"
         f"随后对{company}下周股价走势进行粗略预测（例如上涨/下跌2-3%），并提供总结分析以支持你的预测，给出卖出理由。"
    )

    # 新增：安全获取有效分析内容（反向遍历chat_messages获取最后一条非TERMINATE消息）
    analysis_content = ""
    #DebugPrinter().debug_print(f"Assistant chat messages: {assistant.user_proxy.chat_messages}")  # 调试打印对话历史
    # 反向遍历获取最后一条非TERMINATE消息
    #DebugPrinter().debug_print(
    #    f"Total chat messages: {type(assistant.user_proxy.chat_messages)}")
    # 遍历消息列表，提取内容
    all_messages = []
    for msg_list in assistant.user_proxy.chat_messages.values():
        all_messages.extend(msg_list)
        
    # 反向遍历所有消息，查找最后一条非TERMINATE的有效内容
    for msg in reversed(all_messages[1:]):
        # 确保消息是字典且包含content字段（过滤工具调用等非文本消息）
        if isinstance(msg, dict) and "content" in msg:
            content = msg["content"]
            DebugPrinter().debug_print(f"Processing message content: {content}")  # 调试打印内容            
            
            # 处理content为列表的情况（如工具返回的多段内容）
            if isinstance(content, list):
                 content_str = "\n".join(content).strip()  # 替换空格为换行符
            else:
                content_str = str(content).strip()
            # 过滤空内容和TERMINATE标记
            if content_str and content_str != "TERMINATE" and "积极进展" in content_str:
                analysis_content += content_str + "\n" # 使用append添加内容

    if "" == analysis_content:
        analysis_content = "无有效分析结果"
    
    DebugPrinter().debug_print(f"Analysis content: {analysis_content}")  
    assistant.reset()  # 重置助手状态（需在获取历史后执行）
    
    # 新增：校验内容非空后生成PDF
    
    # 新增：校验内容非空后生成PDF（关键修改2：HTML样式保留换行）
    if "无有效分析结果" not in analysis_content:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{company}股价分析报告</title>
            <style>
                /* 关键修改：设置white-space保留换行符 */
                div {{ 
                    font-size: 14px; 
                    line-height: 1.6; 
                    white-space: pre-wrap;  /* 保留换行和空格 */
                }}
            </style>
        </head>
        <body>
            <h1>{company}股价分析报告</h1>
            <p>生成时间：{get_current_date()}</p>
            <div>{analysis_content}</div>  <!-- 直接使用带换行符的内容 -->
        </body>
        </html>
        """
        pdf_path = f"/root/project/FinRobot/myfinrobot/test_tutorial/{company}_analysis_{get_current_date()}.pdf"
        pdfkit.from_string(html_template, pdf_path)
    else:
        print("警告：未获取到有效分析结果，PDF生成跳过")
         
    pass

if __name__ == "__main__":
    main()