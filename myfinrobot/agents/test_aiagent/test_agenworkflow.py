import unittest
from autogen import UserProxyAgent, GroupChatManager
from myfinrobot.agents.workflow import (
    FinRobot,
    SingleAssistant,
    SingleAssistantRAG,
    MultiAssistantWithLeader
)
from myfinrobot.toolkits import register_toolkits

class TestFinancialTools:
    @staticmethod
    def get_stock_pe(symbol: str) -> float:
        '''获取股票市盈率'''
        return 25.3 if symbol == "NVDA" else 18.7

class TestEnhancedWorkflow(unittest.TestCase):
    
    def setUp(self):
        # 公共配置（使用真实LLM服务，需替换为实际可用的配置）
        self.llm_config = {
            'config_list': [{
                "model": "deepseek-chat",
                "api_key": "sk-2272aa47f3b3484aa0c75511ac65ee43",  # 替换为真实API Key
                "base_url": "https://api.deepseek.com/v1"
            }]
        }

    #@unittest.skip("暂时禁止")
    def test_enhanced_rag(self):
        '''测试增强型RAG工作流（实际调用）'''
        # 使用真实RAG配置（需确保./financial_db路径存在且有数据）
        analyst = SingleAssistantRAG(
            agent_config='Market_Analyst',
            llm_config=self.llm_config,
            retrieve_config={'db_path': './financial_db'},  # 替换为真实数据库路径
            rag_description='财务数据分析'
        )
        
        # 实际调用chat方法（需确保LLM服务可用）
        analyst.chat("NVDA的市盈率是多少？")
        
        # 验证RAG是否被触发（通过检查聊天记录）
        chat_history = analyst.assistant.get_chat_history(analyst.user_proxy)
        self.assertIn("RAG结果", chat_history[-1]['content'], "RAG未正确集成")

    @unittest.skip("暂时禁止")
    def test_leadership_flow(self):
        '''测试领导决策流程（实际团队协作）'''
        # 创建真实团队实例
        team = MultiAssistantWithLeader(
            group_config={
                'name': '投资决策委员会',
                'agents': ['Market_Analyst', 'Expert_Investor']
            },
            llm_config=self.llm_config
        )
        
        # 验证组织结构（真实实例类型）
        self.assertIsInstance(team.leader, FinRobot, "组长应为FinRobot实例")
        self.assertEqual(len(team.agents), 2, "应包含2个成员")
        
        # 实际触发决策对话（需确保LLM服务可用）
        team.chat("决定Q2投资组合调整方案")
        
        # 验证消息流转（检查聊天记录长度）
        chat_history = team.leader.get_chat_history(team.user_proxy)
        self.assertGreater(len(chat_history), 1, "未触发团队对话")

    @unittest.skip("暂时禁止")
    def test_e2e_investment_process(self):
        '''端到端投资分析流程（真实工具调用）'''
        # 注册真实金融工具
        register_toolkits(
            [TestFinancialTools.get_stock_pe],
            caller=UserProxyAgent(name="TestCaller"),  # 真实调用代理
            executor=UserProxyAgent(name="TestExecutor")  # 真实执行代理
        )
        
        # 创建真实分析师实例
        analyst = SingleAssistantRAG(
            agent_config='Market_Analyst',
            llm_config=self.llm_config,
            retrieve_config={'db_path': './db'}  # 替换为真实数据库路径
        )
        
        # 实际执行投资分析（需确保LLM服务可用）
        analyst.chat("请分析NVDA投资价值")
        
        # 验证输出结论（检查最终消息）
        last_msg = analyst.user_proxy.last_message()['content']
        self.assertIn("NVDA", last_msg, "未包含目标股票分析")
        self.assertIn("市盈率", last_msg, "未包含关键财务指标")
    
    @unittest.skip("暂时禁止")
    def test_shadow_mode(self):
        '''影子模式验证（无mock）'''
        analyst = SingleAssistant(
            agent_config='Market_Analyst',
            llm_config=self.llm_config
        )
        
        # 验证影子实例属性（真实实例）
        shadow = analyst.assistant_shadow
        self.assertEqual(shadow.name, "Market_Analyst_Shadow", "影子实例命名错误")
        self.assertEqual(len(shadow.toolkits), 0, "影子实例不应携带工具")
        
        # 验证嵌套对话（真实注册记录）
        self.assertEqual(len(analyst.assistant._nested_chats), 1, "应注册1个嵌套对话")

if __name__ == '__main__':
    unittest.main()