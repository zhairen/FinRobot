import unittest
from unittest.mock import patch, MagicMock, mock_open
from autogen import UserProxyAgent
from ..utils import instruction_trigger, instruction_message, order_trigger, order_message

class EnhancedAgentUtilsTest(unittest.TestCase):
    
    def setUp(self):
        # 初始化模拟对象
        self.leader = MagicMock(name='InvestmentLeader')
        self.analyst = MagicMock(name='FinancialAnalyst')
        
        # 配置标准测试消息
        self.valid_file_msg = {
            'content': 'instruction & resources saved to D:/investment_plan.txt'
        }
        self.valid_order_msg = {
            'content': '[QuantTeam] 请实现以下功能：\n1. 开发动量策略\n2. 集成风险模型'
        }

    # region 指令触发测试
    @patch('os.path.exists')
    def test_instruction_trigger_scenarios(self, mock_exists):
        '''测试多场景指令触发逻辑'''
        # 正常场景
        mock_exists.return_value = True
        self.leader.last_message.return_value = self.valid_file_msg
        self.assertTrue(instruction_trigger(self.leader))

        # 文件不存在场景
        mock_exists.return_value = False
        self.assertFalse(instruction_trigger(self.leader), "文件不存在时应返回False")

        # 无效消息格式
        self.leader.last_message.return_value = {'content': '无效消息'}
        self.assertFalse(instruction_trigger(self.leader))
    # endregion

    # region 指令消息生成测试
    @patch('builtins.open', new_callable=mock_open, read_data='战略投资方案')
    def test_instruction_message_generation(self, mock_file):
        '''测试指令消息生成机制'''
        # 正常文件读取
        result = instruction_message(
            recipient=self.analyst,
            messages=[self.valid_file_msg],
            sender=self.leader,
            config=None
        )
        
        # 验证关键要素
        self.assertIn('战略投资方案', result)
        self.assertIn('TERMINATE', result)
        mock_file.assert_called_with('D:/investment_plan.txt', 'r')

        # 异常文件读取测试
        with patch('builtins.open', mock_open()) as mock_fail:
            mock_fail.side_effect = FileNotFoundError
            result = instruction_message(
                recipient=self.analyst,
                messages=[self.valid_file_msg],
                sender=self.leader,
                config=None
            )
            self.assertIn('文件读取失败', result)
    # endregion

    # region 任务触发测试
    def test_order_trigger_pattern_matching(self):
        '''测试多种任务模式匹配'''
        # 标准模式匹配
        self.leader.last_message.return_value = self.valid_order_msg
        self.assertTrue(order_trigger(self.leader, name='InvestmentLeader', pattern='[QuantTeam]'))

        # 大小写敏感测试
        self.leader.last_message.return_value = {'content': '[QUANTTEAM] 任务内容'}
        self.assertFalse(order_trigger(self.leader, name='InvestmentLeader', pattern='[QuantTeam]'))

        # 多团队模式处理
        multi_team_msg = {'content': '[QuantTeam][RiskTeam] 联合任务'}
        self.leader.last_message.return_value = multi_team_msg
        self.assertTrue(order_trigger(self.leader, name='InvestmentLeader', pattern='QuantTeam'))
    # endregion

    # region 任务消息解析测试
    def test_order_message_parsing(self):
        '''测试复杂任务解析逻辑'''
        # 多级任务解析
        nested_order = {
            'content': '''
            [QuantTeam] 开发策略：
            - 子任务1: 数据获取
                * 来源: Bloomberg
                * 频率: 实时
            - 子任务2: 信号生成
            '''
        }
        self.analyst.chat_messages_for_summary.return_value = [nested_order]
        
        result = order_message(
            pattern='QuantTeam',
            recipient=self.analyst,
            messages=None,
            sender=self.leader,
            config=None
        )
        
        self.assertIn('Bloomberg', result)
        self.assertIn('信号生成', result)

        # 带格式错误的订单测试
        malformed_order = {'content': '[QuantTeam 未闭合标签 任务内容'}
        self.analyst.chat_messages_for_summary.return_value = [malformed_order]
        result = order_message(
            pattern='QuantTeam',
            recipient=self.analyst,
            messages=None,
            sender=self.leader,
            config=None
        )
        self.assertEqual(result, str(malformed_order['content']))
    # endregion

    # region 端到端工作流测试
    @patch('builtins.open', new_callable=mock_open, read_data='量化策略开发指南')
    def test_full_investment_workflow(self, mock_file):
        '''完整投资策略开发工作流验证'''
        # 阶段1: 指令触发
        self.leader.last_message.return_value = self.valid_file_msg
        self.assertTrue(instruction_trigger(self.leader))

        # 阶段2: 生成指令
        instruction = instruction_message(
            recipient=self.analyst,
            messages=[self.valid_file_msg],
            sender=self.leader,
            config=None
        )
        self.assertIn('量化策略开发指南', instruction)

        # 阶段3: 任务分派
        self.leader.last_message.return_value = self.valid_order_msg
        self.assertTrue(order_trigger(self.leader, name='InvestmentLeader', pattern='QuantTeam'))

        # 阶段4: 任务解析
        task_content = order_message(
            pattern='QuantTeam',
            recipient=self.analyst,
            messages=None,
            sender=self.leader,
            config=None
        )
        self.assertIn('动量策略', task_content)
        self.assertIn('风险模型', task_content)

        # 阶段5: 执行验证
        self.analyst.reset_mock()
        self.analyst.receive_message(task_content)
        self.analyst.send.assert_called_once()
        
        # 验证消息内容
        sent_msg = self.analyst.send.call_args[0][0]
        self.assertIn('开发动量策略', sent_msg['content'])
        self.assertIn('集成风险模型', sent_msg['content'])
    # endregion

if __name__ == '__main__':
    unittest.main()