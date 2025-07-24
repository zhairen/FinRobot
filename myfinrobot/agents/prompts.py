from textwrap import dedent


leader_system_message = dedent(
    """
    You are the leader of the following group members:
    
    {group_desc}
    
    As a group leader, you are responsible for coordinating the team's efforts to achieve the project's objectives. You must ensure that the team is working together effectively and efficiently. 

    - Summarize the status of the whole project progess each time you respond.
    - End your response with an order to one of your team members to progress the project, if the objective has not been achieved yet.
    - Orders should be follow the format: \"[<name of staff>] <order>\".
    - Orders need to be detailed, including necessary time period information, stock information or instruction from higher level leaders. 
    - Make only one order at a time.
    - After receiving feedback from a team member, check the results of the task, and make sure it has been well completed before proceding to th next order.

    Reply "TERMINATE" in the end when everything is done.
    """
)
role_system_message = dedent(
    """
    As a {title}, your reponsibilities are as follows:
    {responsibilities}

    Reply "TERMINATE" in the end when everything is done.
    """
)
order_template = dedent(
    """
    Follow leader's order and complete the following task with your group members:

    {order}

    For coding tasks, provide python scripts and executor will run it for you.
    Save your results or any intermediate data locally and let group leader know how to read them.
    DO NOT include "TERMINATE" in your response until you have received the results from the execution of the Python scripts.
    If the task cannot be done currently or need assistance from other members, report the reasons or requirements to group leader ended with TERMINATE. 
"""
)


# 新增分析提示模板
analysis_prompt_template = dedent(
    """
    [分析任务模板]
    当前参数：{parameters}
    数据摘要：{data_summary}
    请完成以下分析步骤：
    1. 数据清洗与预处理
    2. 关键指标计算
    3. 生成可视化图表
    4. 撰写分析报告
    """
)

# 新增barra模板
barramodel_prompt_template = dedent(
    """
    [QuantTeam] 专业的量化开发团队，开发多因子模型。
    请构建{model_name}（中国股票）模型，给出完整的代码开发。
    包括：所有核心因子、算法、开发步骤、特殊处理、数据异常处理和输出要求。
    # {model_name}模型（中国股票）
    **核心因子**：
    1. 国家因子：中国市场风险溢价（所有股票暴露为1）
    2. 行业因子：31个申万一级行业哑变量
    3. 风格因子（16个）：
    - 价值：账面市值比（BP）、盈利收益率（EY）
    - 波动：贝塔（BETA）、残差波动率（RESVOL）
    - 收益：股息率（DY）
    - 成长：长期增长预期（LTG）
    - 流动性：换手率（TURN）、流动性冲击（LIQ）
    - 动量：12个月动量（MOM）、长期反转（LREV）
    - 质量：盈利质量（EQ）、投资质量（IQ）、盈利能力（PROF）
    - 规模：对数市值（SIZE）、中盘哑变量（MIDCAP）
    **算法**：
    - 因子计算：基于Wind/CSMAR/Yfinance的日频行情和季度财务数据
    - 因子标准化：z-score标准化
    - 因子中性化：对行业因子进行回归取残差
    - 因子收益率计算：加权最小二乘法（WLS），约束行业因子收益率之和为0
    - 因子协方差矩阵：Newey-West调整（滞后5期）
    **开发步骤**：
    1. **数据准备**：获取2020-2024年全A股/港股数据（剔除ST、*ST、上市不足60天股票）
    2. **因子计算**：计算16个风格因子和31个行业因子
    3. **数据处理**：
    a. 缺失值：行业均值填充
    b. 极值：3倍标准差缩尾
    c. 标准化：z-score
    d. 中性化：对行业因子回归取残差
    4. **模型求解**：
    a. 构建因子暴露矩阵
    b. 用WLS求解因子收益率（日频）
    c. 计算因子协方差矩阵（Newey-West调整）
    5. **风险预测**：
    a. 个股总风险 = sqrt(因子风险 + 特质风险)
    b. 组合风险 = sqrt(X'FX + Δ)，其中X为因子暴露，F为因子协方差矩阵，Δ为特质风险
    **特殊处理**：
    - 财务数据时滞：季度报告数据延迟1-2个月生效
    - 涨停板影响：连续涨停股票剔除流动性因子计算
    - 新上市股票：上市前60天不纳入模型
    - 因子正交化：Gram-Schmidt过程消除因子间相关性
    - 行业轮动：每季度末动态调整行业分类
    **数据异常处理**：
    1. 极端值检测：MAD（中位数绝对偏差），阈值±5倍MAD
    2. 缺失值处理流程：
    - 行业数据缺失 → 用行业均值填充
    - 宏观数据缺失 → 用移动平均填充
    - 其他数据缺失 → 删除观测值
    3. 幸存者偏差：包含已退市股票数据
    **输出要求**：
    1. implementation_code 代码：
    - 包含所有因子计算、模型构建和风险预测的完整Python实现
    - 代码需有详细注释，便于理解和复现
    - 提供可执行脚本和依赖库列表
    2. 数据输出：
    - 因子暴露矩阵（2020-2024）
    - 因子收益率矩阵（12个月滚动）
    - 因子协方差矩阵（动态调整）
    - 风险预测结果（个股和组合）       
    3. 分析报告：
    - 因子收益率时序图（2020-2024）
    - 因子IC分析表（信息系数）
    - 因子相关性矩阵热力图
    - 风险归因报告（国家/行业/风格风险占比）
    4. 绩效指标：
    - 平均因子收益率
    - 因子波动率
    - 因子夏普比率
    - 特质风险解释力（R²）
    5. 可视化：
    - 动态因子暴露仪表盘
    - 行业风险热力图
    - 组合风险分解旭日图    
    # 注意
    - 以上构建模型要求用Python实现核心算法，并提供完整代码和报告。
    - 数据源需明确标注（如Wind、Bloomberg、yfinance、tushare等）。
    - 所有处理步骤必须有可验证的数学或算法依据。
    """
)


# 新增barra模板
barramodel_prompt_template_global = dedent(
    """
    [QuantTeam] 专业的量化开发团队，开发多因子模型。
    请构建{model_name}（全球市场）模型，完成完整的代码开发。
    包括：所有核心因子、算法、开发步骤、特殊处理、数据异常处理和输出要求。
    # {model_name}模型（全球市场）
    **核心因子**：
    1. 全球因子：全球市场收益率（MKT）
    2. 国家因子：美/中/欧/日等12个主要经济体哑变量
    3. 行业因子：GICS全球11个一级行业
    4. 货币因子：美元/欧元/日元等8种货币敞口
    5. 风格因子（7类）：
    - 市场贝塔（BETA_GLOBAL）
    - 规模（SIZE_GLOBAL）
    - 价值（BP_GLOBAL, EP_GLOBAL）
    - 动量（MOM_GLOBAL）
    - 质量（ROE_GLOBAL, LEV_GLOBAL）
    - 波动率（VOL_GLOBAL）
    - 流动性（LIQ_GROUP）
    6. 宏观扩散因子：
    - PMI扩散指数（PMI_DIFF）
    - CPI扩散指数（CPI_DIFF）
    **算法**：
    - 因子计算：全球标准化（如BP因子按全球横截面标准化）
    - 动量因子：国家内相对强度排名
    - 宏观扩散因子：PMI变化方向（当前值减3月移动平均）
    - 因子收益率求解：Robust回归（Huber损失函数）
    - 协方差矩阵：DCC-GARCH动态相关性建模
    **开发步骤**：
    1. **数据整合**：获取MSCI全球指数成分股（25国）、主权债、宏观数据（OECD）、汇率（BIS）
    2. **资产映射**：
    - 股票：GLOBAL风格因子
    - 主权债：久期因子+信用利差因子
    - 商品：通胀beta+地缘敏感度
    - 货币：利差因子+风险溢价
    3. **因子计算**：
    a. 计算全球统一风格因子
    b. 生成国家/行业/货币因子
    c. 合成宏观扩散因子
    4. **模型构建**：
    a. 分层建模：全球因子→国家因子→行业因子→风格因子→货币因子→宏观扩散因子
    b. 因子收益率求解：Robust回归
    c. 协方差矩阵：DCC-GARCH
    5. **资产配置**：
    a. 风险预算分配：风险平价核心逻辑
    b. 宏观信号整合：
        - PMI_DIFF>0 → 股票权重+10%
        - CPI_DIFF<0 → 债券权重+15%
        - 地缘风险>阈值 → 黄金权重+20%
    **特殊处理**：
    - 时区对齐：统一UTC+0时间戳
    - 货币转换：所有资产以SDR（特别提款权）计价
    - 地缘政治溢价：合成指数=0.3*冲突指数+0.7*能源依赖度
    - 流动性分层：新兴市场股票流动性折扣系数0.7
    - ESG整合：气候转型风险因子（CTR）作为特质风险调整项
    **数据异常处理**：
    1. 跨市场数据冲突：优先采用BIS/IMF数据，偏差>5%触发警报
    2. 非同步交易：Scholes-Williams贝塔修正（β_corrected = β_observed/(1+0.5*σ_market^2)）
    3. 缺失数据：
    - 宏观数据：状态空间模型预测填充
    - 公司数据：全球行业均值填充
    4. 极端事件过滤：2020疫情、2022俄乌冲突、2025台海危机（模拟）
    **输出要求**：
    1. 核心输出：
    - 全球因子收益率矩阵（12个月滚动）
    - 资产-因子映射关系表
    - 货币风险敞口报告
    - 宏观敏感度分析（PMI/CPI冲击测试）
    2. 可视化：
    - 三维风险地图（国家/行业/风格）
    - 动态风险预算分配树图
    - 因子相关性时变图（2020-2024）
    3. 绩效评估：
    | 指标          | 目标值  |
    |---------------|---------|
    | 年化波动率    | <12%    |
    | 夏普比率      | >1.2    |
    | 最大回撤      | <20%    |
    | 国家风险贡献  | ≤30%    |
    | 货币风险      | ≤10%    |
    4. 压力测试报告：
    - 情景1：美联储加息300bp
    - 情景2：中国GDP增速降至3%
    - 情景3：中东全面冲突爆发
    5. implementation_code 代码：
    - 包含所有因子计算、模型构建和风险预测的完整Python实现
    - 代码需有详细注释，便于理解和复现
    - 提供可执行脚本s和依赖库列表    
    # 注意
    - 以上构建模型要求用Python实现核心算法，并提供完整代码和报告。
    - 数据源需明确标注（如Wind、Bloomberg、yfinance等）。
    - 所有处理步骤必须有可验证的数学或算法依据。
    """
)
