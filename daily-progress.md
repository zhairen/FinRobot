## 2025-7-9
- 开发yfinance最小功能集
- 准备先实现个最小demo，如data-source文件夹中yfinance获取数据，处理股票，调用aiagent，生产tutorial-beginner里的一个示例报告。
- 请将各个部分编写为引擎，DataEngine，AnalysisEngine，AgentEngine，ReportEngine。数据引擎，分析引擎，大模型引擎和报告引擎。
- 初步创建DataEngine,并测试

## 2025-7-10
- AnalysisEngine，AgentEngine，ReportEngine。数据引擎，分析引擎，大模型引擎和报告引擎。
- 初步创建AnalysisEngine,并测试
- prompt请重写StrategyEngine，我这里的StrategyEngine是在初步DataEngine之后，参考functional文件夹的宽泛的投资分析处理引擎的概念。
- chat 提醒了选择合适的设计模式
- 初步完成DataEngine加入设计模式的改造
- 开始实现STrategyEngine处理functional功能，AI给出的初步内容graph TD
    A[StrategyEngine] --> B[AnalyzerStrategy]
    A --> C[QuantitativeStrategy]
    A --> D[RiskStrategy]
    A --> E[VisualizationStrategy]
    B --> F[ReportAnalysisUtils]
    C --> G[BackTraderUtils]
    D --> H[RiskUtils]
    E --> I[MplFinanceUtils]
- 先实现了StrategyEngine的利润表策略，以此为demo后续开始aiagent过程。
- TestStrategyEngine测试获取NVDA的财报利润表。

## 2025-7-11
- 设计模式设计agents，了解agents原有结构，支持多种模式，配置实现分开，支持依赖注入 dataengine和strategyengine
- ds代码开发设计模式
- 类图，文件结构图 
- 根据现在的文件结构、类图和功能需求，更正完善代码。Dataengine和srategyengine依赖注入，支持多种大模型。尽可能引用现在的agent_library,prompts,utils,workflow里现有的实现即可。更正错误和完善代码，除agent_library,prompts,utils,workflow 4个文件外，该agents文件夹下所有文件。
- 测试dsapi完成初步模型回答。但原来agents功能可以生成pdf等，绘图等，显然更强大。

## 2025-7-12
- 继续完善aiagentengine
- 研究agents文件夹下文件，英文翻译中文
- agents的大模型明显还有生成图标和文件需要添加
- 由于agents是核心，4个文件逐个细读拆解。
- 后面还有的任务有，图表实现，fastapiweb端，数据库存储与查询。
- ai prompts请在test_aiagent中开发实现test_agentutils.py，测试使用该utils.py文件各功能。 需要构造一个示例场景，金融投资agent，展示如何配置智能体并使用这些工具函数。例如，创建一个组领导智能体和一个程序员智能体，当组长发送包含文件路径的消息时，触发instruction_message读取文件内容，并生成任务指令。然后，当组长发送特定格式的指令时，使用order_trigger检测并解析出具体任务内容。
- 生成了测试单元代码，运行test_agentutils，实现barra cne6多因子模型,完成了本功能的测试
- 后续继续test-agents那4个文件的测试

## 2025-7-13
- 插队实现外汇行情，以便后续和fastapi快速开发完成并上线
- prompts参考架构dataengine，strategyengine，agentengine 数据源，处理分析，大模型代理的过程，之前是股票，请按该过程添加外汇资产，并单独新建py文件。请给出架构设计，类图，功能需求和详细代码实现。

## 2025-7-14
- 添加了外汇代码，未开发测试

## 2025-7-15
- 熟悉外汇模块包含功能项
- 暂停外汇模块开发

## 2025-7-16
- 完成测试验证test_agentutils最后一个函数不验证了，因为步骤和之前一样。
- 继续测试验证test_agentworkflow
- tradeview站看起来很强大
- 垂直、深入、专项优势是什么
- 初步完成了这几项，需要考虑将该agent如何并入fastapi的web项目中
- 测试自行编写的test-agents示例代码特别慢，开始用tutorials_advanced里面的示例。熟悉代码和测试。

## 2025-7-17
- 运行了官方demo生成pdf  testreport testtutorial

## 2025-7-18
- 生成了wmt 股票分析报告，支持中文
- 了解到有个openbb和彭博类似的开源终端
- 搭建个人平台 IP 系统 产品
- 继续begin tutorial
- 考虑怎么融入fastapi web端，进行web端支持的fintech的aigent的robot

## 2025-7-29
- 继续begin tutorial，升级maker-pdf

## 2025-7-20
- 升级maker-pdf github maker版不报错
- 运行finance_llm

## 2025-7-21
- cashflow平台的model不错
- nvda tulpia nvda

## 2025-7-22
- 保存requirement.
- 运行成功agent_rag_earning_call.
- 安装了windsurf 辅助编程AI
- 多模型多chat

## 2025-7-23
- 了解了下整合入fastapi react full stack框架
- ipynb
- 再新建项目过程中要记录步骤，命令

## 2025-7-24
- 熟悉openbb和full-stack-fastapi后
- 该finrobot初步均部署完成，小部分改造。
- ai agent是两点

## 2025-7-25
- 暂停该项目，等我完成了前后端全栈的搭建
- 再集成该ai agent 或openbb












