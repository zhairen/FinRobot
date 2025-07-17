from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile

from autogen import UserProxyAgent
from myfinrobot.agents.utils import (
    instruction_trigger,
    instruction_message,
    order_trigger,
    order_message
)
from myfinrobot.agents.workflow import FinRobot, SingleAssistant
from myfinrobot.debugprinter import DebugPrinter
from myfinrobot.agents.prompts import barramodel_prompt_template

class EnhancedFinancialUtilsTest(unittest.TestCase):
    
    def setUp(self):
        #（新增LLM配置）
        base_config = {
            "config_list": [{
                "model": "deepseek-chat",
                "api_key": "sk-2272aa47f3b3484aa0c75511ac65ee43",
                "base_url": "https://api.deepseek.com/v1",  # DeepSeek API 端点  
                "max_tokens": 1000             
            }],
            "timeout": 600
        }
        
        self.user_proxy = UserProxyAgent(
            name="TestProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=15, 
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),   
            system_message="测试代理")  
        
        # 初始化真实文件环境
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, 'fin_task.txt')
        DebugPrinter().debug_print(
            f"Test file created at:{self.test_file}")

        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('''量化策略开发任务书
                    1. 数据准备阶段
                        - 获取全A股2020-2024年数据（Wind/CSMAR/Bloomberg/YFinance）
                        - 包含已退市股票数据
                        - 财务数据时滞处理                        
                    2. 因子工程阶段
                        - 计算所有风格因子
                        - 行业哑变量处理
                        - 因子标准化(z-score)
                        - 中性化处理（行业回归）                        
                    3. 模型构建阶段
                        - WLS求解因子收益率
                        - Newey-West协方差调整
                        - 风险预测模型 
                        - 完整多因子模型代码
                        - 生成因子暴露矩阵代码
                        - 生成因子暴露矩阵
                        - 生成协方差矩阵代码
                        - 生成协方差矩阵                       
                    4. 回测验证阶段
                        - 多空组合回测
                        - 因子IC分析
                        - 风险归因报告''')

        # 初始化真实智能体实例
        self.leader = FinRobot(
            agent_config={
                "name": "Investment_Leader",
                "profile": "金融投资组负责人"
            },
             llm_config=base_config  # 新增配置
        )
        DebugPrinter().debug_print(
            f"Leader agent : {self.leader}")
        
        self.analyst = SingleAssistant(
            agent_config={
                "name": "Quant_Analyst",
                "profile": "量化策略分析师"
            },
            llm_config=base_config  # 新增配置
        )
        
       # 改用正确的消息订阅方式
        # self.leader.register_hook(
        #     'message_received', 
        #     lambda msg: self.analyst.receive(msg)
        # )
        # 配置标准测试消息
        self.valid_msg = {
            "content": f"instruction & resources saved to {self.test_file}"
        }
                
   # 新增的分块发送方法
    def send_in_chunks(self, recipient, message_content, chunk_size=10000):
        """将长消息分块发送"""
        # 分块发送消息
        total_chunks = (len(message_content) // chunk_size) + 1
        
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            chunk = message_content[start_idx:end_idx]
            
            # 添加分块标记
            chunk_msg = {
                "content": f"[分块 {i+1}/{total_chunks}]\n{chunk}",
                "role": "user"
            }
            
            # 发送分块
            self.user_proxy.send(
                recipient=recipient,
                message=chunk_msg,
                request_reply=(i == total_chunks - 1)  # 只在最后一块请求回复
            )
            
            # 如果不是最后一块，暂停等待处理
            if i < total_chunks - 1:
                self.leader.generate_reply(messages=[chunk_msg], sender=self.user_proxy)
    

    # region 强化订单处理 Done
    @unittest.skip("已测试通过暂时禁止")
    def test_complex_order_parsing(self):
        '''测试复杂金融模型解析'''
        test_order = {
            "content": barramodel_prompt_template.format(
            model_name="BARRA CNE6") 
            + " 任务完成后，在最后一行回复：'TERMINATE'",
            "role": "user"
        }
        self.leader.reset()
         # 先发送消息初始化对话历史
        # 发送消息并等待回复
        self.user_proxy.initiate_chat(
            recipient=self.leader,
            message=test_order,
            max_tokens=1000,
            clear_history=True
        )
        
        # 使用分块发送方法
        #self.send_in_chunks(self.analyst.assistant, test_order["content"])

        
        # 获取实际生成的对话记录
        actual_messages = self.leader.get_chat_history(self.user_proxy)
        #actual_messages = self.analyst.assistant.get_chat_history(self.user_proxy)

        #DebugPrinter().debug_print(f"Last message content: {actual_messages[-1]['content']}")
        lst_messages = ""
        #舍弃第一个actual_messages
        actual_messages = actual_messages[1:]  # 舍弃第一个消息（通常是系统消息或提示）
        for msg in actual_messages:
            if 'content' in msg:
                # 确保消息内容存在
                if isinstance(msg['content'], list):
                    #处理msg['content']中的转义字符和\n
                    #msg['content'] = [m.replace('\\n', '\n') for m in msg].get('content', [])
                    #舍弃第一个，因为是prompts
                    
                    # 如果是列表，合并为字符串
                    lst_messages += ' '.join(msg['content'])
                else:
                    # 如果是字符串，直接添加
                    lst_messages += msg['content']
        DebugPrinter().debug_print(f"All messages: {lst_messages}")
        # 修正参数顺序和消息选择
        # parsed = order_message(
        #     sender=self.user_proxy,
        #     recipient=self.analyst.assistant,
        #     messages=actual_messages[-1:] if actual_messages else [],  # 确保取最新消息
        #     pattern="QuantTeam",
        #     config=None
        # )

        # DebugPrinter().debug_print(
        #     f"Parsed order: {parsed}")
        # self.assertIn("动量", parsed)
        
        # 获取完整的消息历史而非仅最后一条
        #all_messages = self.recipient.chat_messages_for_summary(self.sender)
        #DebugPrinter().debug_print(f"All messages: {all_messages}")
        # 在所有消息中查找实际订单内容
                
        # 验证订单内容
        self.assertIn("动量", lst_messages, "订单消息中缺少'动量'关键词")

        save_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'experiments', 
            'quant_strategies'
        ))
        os.makedirs(save_dir, exist_ok=True)
        
        # 新增的深度断言
        self.assertIn('Python实现', lst_messages, "缺少代码实现部分")

        # 使用实际解析结果
        code_content = f"""
        # Auto-generated MultiFactor Model
        {lst_messages}
                
        """

        # 带时间戳的文件名
        filename = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(os.path.join(save_dir, filename), 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        self.assertIn("CNE6", code_content, "缺少Barra CNE6模型类")
        self.assertIn("协方差矩阵", code_content, "缺少协方差计算逻辑")
    # endregion

    # region 增强型指令测试 Done
    @unittest.skip("暂时禁用")
    def test_instruction_scenarios(self):
        '''测试多场景指令触发'''
       # 正常场景
        self.leader.test_file = self.test_file  # 新增路径绑定
        self.leader.last_message = lambda: self.valid_msg
        DebugPrinter().debug_print(
            f"Testing with valid message: {self.leader.last_message()}")
        self.assertTrue(instruction_trigger(self.leader))

        # 文件不存在场景
        original_path = self.leader.test_file
        self.leader.test_file = "/invalid/path/fake_file.txt"
        DebugPrinter().debug_print(
            f"Testing with invalid file path: {self.leader.test_file}")
        #instruction_trigger(self.leader)
        DebugPrinter().debug_print(
            f"Current test file path: {instruction_trigger(self.leader)}")
        #self.assertFalse(instruction_trigger(self.leader))
        self.leader.test_file = original_path  # 恢复路径

        # 异常消息格式
        self.leader.last_message = lambda: {"content": "无效指令"}
        DebugPrinter().debug_print(
            f"Testing with invalid message format: {self.leader.last_message()}")
        DebugPrinter().debug_print(
            f"Current last message content: {instruction_trigger(self.leader)}")
        self.assertFalse(instruction_trigger(self.leader))


        # 验证真实消息处理流程
        actual_messages = self.leader.get_chat_history(self.user_proxy)
        DebugPrinter().debug_print(f"Actual messages: {actual_messages}")
        #self.assertGreater(len(actual_messages), 0)
        #self.assertIn(self.valid_msg['content'], actual_messages[-1]['content'])
    # endregion

    # region 强化消息处理 Done
    @unittest.skip("暂时禁用")
    def test_instruction_handling(self):  # 移除@patch装饰器
        '''测试指令消息生成机制'''
        self.leader.test_file = self.test_file  # 新增路径绑定
        self.leader.last_message = lambda: self.valid_msg
        DebugPrinter().debug_print(
            f"Testing with valid message: {self.leader.last_message()}")
        self.assertTrue(instruction_trigger(self.leader))

        # 关键修复：通过user_proxy直接向analyst发送消息（框架自动记录聊天记录）
        self.user_proxy.send(
            recipient=self.analyst.assistant,  # 直接发送给analyst
            message=self.valid_msg,
            request_reply=False  # 请求analyst回复
        )

        # 正常文件读取（使用setUp中创建的临时文件）
        with open(self.test_file, 'r', encoding='utf-8') as f:
            expected_content = f.read()
        
        
        # 此时analyst的聊天记录已自动包含user_proxy发送的消息
        result = instruction_message(
            recipient=self.analyst.assistant,  # 确保recipient是analyst实例
            messages=[self.valid_msg],
            sender=self.user_proxy,  # 发送者是user_proxy（与实际消息来源一致）
            config=None
        )

        self.assertIn("量化策略开发任务书", result)  # 验证包含文件核心内容
        self.assertIn("TERMINATE", result)  # 验证终止标记
       
    # endregion

    # region 端到端流程验证
    #@unittest.skip("暂时禁用")
    def test_full_workflow(self):  # 移除@patch装饰器和mock_proxy参数
        '''完整投资策略开发流程'''
        # 阶段1: 指令触发
        self.leader.last_message = lambda: self.valid_msg
        self.assertTrue(instruction_trigger(self.leader))

        # 阶段2: 生成指令（使用真实文件内容）
        with open(self.test_file, 'r', encoding='utf-8') as f:
            expected_content = f.read()
        instruction = instruction_message(
            recipient=self.analyst.assistant,
            messages=[self.valid_msg],
            sender=self.leader,
            config=None
        )
        self.assertIn(expected_content.strip(), instruction.strip())  # 验证指令包含文件内容

        # 阶段3: 任务执行验证（使用真实user_proxy发送消息）
        self.user_proxy.initiate_chat(
            recipient=self.leader,
            message=self.valid_msg,
            max_tokens=1000,
            clear_history=True
        )
        actual_messages = self.leader.get_chat_history(self.user_proxy)
        self.assertGreater(len(actual_messages), 1, "对话历史应包含交互消息")

        # 阶段4: 结果验证（假设analyst处理后会有回复）
        # 实际需根据业务逻辑调整断言（示例验证消息存在）
        analyst_messages = self.analyst.get_chat_history(self.user_proxy)
        if analyst_messages:
            self.assertIn("处理中", analyst_messages[-1]['content'])
    # endregion

    def tearDown(self):
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
