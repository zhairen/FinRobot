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

