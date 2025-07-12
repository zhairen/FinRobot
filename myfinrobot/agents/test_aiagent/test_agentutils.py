import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
from myfinrobot.agents.utils import (
    instruction_trigger,
    instruction_message,
    order_trigger,
    order_message
)
from myfinrobot.agents.workflow import FinRobot, SingleAssistant

class EnhancedFinancialUtilsTest(unittest.TestCase):
    
    def setUp(self):
        # 初始化真实文件环境
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, 'fin_task.txt')
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('量化策略开发任务书\n1. 数据采集\n2. 因子计算\n3. 回测验证')

        # 初始化真实智能体实例
        self.leader = FinRobot(
            agent_config={
                "name": "Investment_Leader",
                "profile": "金融投资组负责人"
            }
        )
        self.analyst = SingleAssistant(
            agent_config={
                "name": "Quant_Analyst",
                "profile": "量化策略分析师"
            }
        )

        # 配置标准测试消息
        self.valid_msg = {
            "content": f"instruction & resources saved to {self.test_file}"
        }

    # region 增强型指令测试
    @patch('os.path.exists')
    def test_instruction_scenarios(self, mock_exists):
        '''测试多场景指令触发'''
        # 正常场景
        mock_exists.return_value = True
        self.leader.last_message.return_value = self.valid_msg
        self.assertTrue(instruction_trigger(self.leader))

        # 文件不存在场景
        mock_exists.return_value = False
        self.assertFalse(instruction_trigger(self.leader))

        # 异常消息格式
        self.leader.last_message.return_value = {"content": "无效指令"}
        self.assertFalse(instruction_trigger(self.leader))
    # endregion

    # region 强化消息处理
    @patch('builtins.open', new_callable=mock_open, read_data='紧急任务: 分析美联储利率决议')
    def test_instruction_handling(self, mock_file):
        '''测试指令消息生成机制'''
        # 正常文件读取
        result = instruction_message(
            recipient=self.analyst.assistant,
            messages=[self.valid_msg],
            sender=self.leader,
            config=None
        )
        self.assertIn("利率决议", result)
        self.assertIn("TERMINATE", result)

        # 带BOM文件读取测试
        with patch('builtins.open', mock_open(read_data='\ufeff带BOM内容')):
            result = instruction_message(...)
            self.assertIn("带BOM内容", result)
    # endregion

    # region 强化订单处理
    def test_complex_order_parsing(self):
        '''测试复杂金融订单解析'''
        # 多级任务订单
        multi_level_order = {
            "content": """
            [QuantTeam] 开发多因子模型：
            - 因子列表:
              * 动量因子
              * 价值因子
            - 回测要求:
              1. 2018-2023年数据
              2. 每日调仓
            """
        }
        self.leader.last_message.return_value = multi_level_order
        
        # 触发并解析
        self.assertTrue(order_trigger(self.leader, name="Investment_Leader", pattern="QuantTeam"))
        parsed = order_message(
            pattern="QuantTeam",
            recipient=self.analyst.assistant,
            messages=None,
            sender=self.leader,
            config=None
        )
        self.assertIn("动量因子", parsed)
        self.assertIn("每日调仓", parsed)
    # endregion

    # region 端到端流程验证
    @patch('myfinrobot.agents.workflow.UserProxyAgent')
    def test_full_workflow(self, mock_proxy):
        '''完整投资策略开发流程'''
        # 阶段1: 指令触发
        self.leader.last_message.return_value = self.valid_msg
        self.assertTrue(instruction_trigger(self.leader))

        # 阶段2: 生成指令
        with open(self.test_file, 'r') as f:
            expected_content = f.read()
        instruction = instruction_message(...)
        self.assertIn(expected_content, instruction)

        # 阶段3: 任务执行验证
        mock_proxy.return_value.send.assert_called_once()
        sent_message = mock_proxy.return_value.send.call_args[0][0]
        self.assertIn("量化策略", sent_message['content'])

        # 阶段4: 结果验证
        mock_proxy.return_value.last_message.return_value = "策略回测完成，夏普比率2.1"
        self.assertIn("夏普比率", self.analyst.user_proxy.last_message())
    # endregion

    def tearDown(self):
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()