import unittest
from unittest.mock import patch, MagicMock
from autogen import UserProxyAgent, GroupChatManager
from ..workflow import (
    FinRobot,
    SingleAssistant,
    SingleAssistantRAG,
    MultiAssistantWithLeader
)
from ...toolkits import register_toolkits

class FinancialTools:
    @staticmethod
    def get_stock_pe(symbol: str) -> float:
        '''获取股票市盈率'''
        return 25.3 if symbol == "NVDA" else 18.7

class TestEnhancedWorkflow(unittest.TestCase):
    
    def setUp(self):
        # 公共配置
        self.llm_config = {
            'config_list': [{'model': 'gpt-4', 'base_url': 'http://localhost:1234/v1'}]
        }
        
        # Mock RAG函数
        self.mock_rag = MagicMock()
        self.mock_rag.side_effect = lambda query: f"RAG结果: {query}"

    @patch('myfinrobot.agents.workflow.get_rag_function')
    def test_enhanced_rag(self, mock_rag):
        '''测试增强型RAG工作流'''
        # 配置mock RAG
        mock_rag.return_value = (self.mock_rag, MagicMock())
        
        # 创建分析师实例
        analyst = SingleAssistantRAG(
            agent_config='Market_Analyst',
            llm_config=self.llm_config,
            retrieve_config={'db_path': './financial_db'},
            rag_description='财务数据分析'
        )
        
        # 验证RAG集成
        analyst.chat("NVDA的市盈率是多少？")
        self.mock_rag.assert_called_once_with("NVDA的市盈率是多少？")
        
        # 验证工具组合
        self.assertEqual(len(analyst.assistant.toolkits), 3, "应包含3个默认工具")

    @patch('myfinrobot.agents.workflow.GroupChatManager')
    def test_leadership_flow(self, mock_manager):
        '''测试领导决策流程'''
        # 配置领导团队
        team = MultiAssistantWithLeader(
            group_config={
                'name': '投资决策委员会',
                'agents': ['Market_Analyst', 'Expert_Investor']
            },
            llm_config=self.llm_config
        )
        
        # 验证组织结构
        self.assertIsInstance(team.leader, FinRobot, "组长应为FinRobot实例")
        self.assertEqual(len(team.agents), 2, "应包含2个成员")
        
        # 模拟决策流程
        with patch.object(UserProxyAgent, 'initiate_chat') as mock_chat:
            team.chat("决定Q2投资组合调整方案")
            
            # 验证消息流转
            args, kwargs = mock_chat.call_args
            self.assertIn('投资组合', kwargs['message'], "应包含投资主题")
            
            # 验证团队工具
            self.assertTrue(hasattr(team.leader, 'toolkits'), "组长应具备工具集")

    def test_e2e_investment_process(self):
        '''端到端投资分析流程'''
        # 注册金融工具
        register_toolkits([FinancialTools.get_stock_pe], 
                        caller=MagicMock(), 
                        executor=MagicMock())
        
        # 创建分析师实例
        analyst = SingleAssistantRAG(
            agent_config='Market_Analyst',
            llm_config=self.llm_config,
            retrieve_config={'db_path': './db'}
        )
        
        # 执行完整对话流程
        with patch.object(UserProxyAgent, 'initiate_chat') as mock_chat:
            mock_chat.return_value = MagicMock(last_message=lambda: "最终建议: 增持NVDA")
            analyst.chat("请分析NVDA投资价值")
            
            # 验证输出结论
            last_msg = analyst.user_proxy.last_message()
            self.assertIn("增持", last_msg, "应包含投资建议")

    def test_shadow_mode(self):
        '''影子模式验证'''
        analyst = SingleAssistant(
            agent_config='Market_Analyst',
            llm_config=self.llm_config
        )
        
        # 验证影子实例
        shadow = analyst.assistant_shadow
        self.assertEqual(shadow.name, "Market_Analyst_Shadow", "影子实例命名错误")
        self.assertEqual(len(shadow.toolkits), 0, "影子实例不应携带工具")
        
        # 验证嵌套对话
        self.assertEqual(len(analyst.assistant._nested_chats), 1, "应注册1个嵌套对话")

if __name__ == '__main__':
    unittest.main()