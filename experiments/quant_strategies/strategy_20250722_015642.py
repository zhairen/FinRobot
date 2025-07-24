
        # Auto-generated MultiFactor Model
        # BARRA CNE6 模型实现

下面我将提供一个完整的Python实现，包括数据准备、因子计算、模型构建和风险预测等步骤。

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import zscore
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 数据准备模块
class DataPreprocessor:
    def __init__(self, start_date='2020-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.industry_mapping = None
        
    def load_price_data(self, filepath):
        """加载价格数据"""
        price_data = pd.read_csv(filepath, parse_dates=['date'])
        price_data = price_data[(price_data['date'] >= self.start_date) & 
                               (price_data['date'] <= self.end_date)]
        return price_data
    
    def load_financial_data(self, filepath):
        """加载财务数据"""
        financial_data = pd.read_csv(filepath, parse_dates=['report_date'])
        return financial_data
    
    def load_industry_data(self, filepath):
        """加载行业数据"""
        industry_data = pd.read_csv(filepath)
        self.industry_mapping = industry_data.set_index('stock_code')['industry'].to_dict()
        return industry_data
    
    def clean_data(self, price_data, financial_data):
        """数据清洗"""
        # 剔除ST/*ST股票
        price_data = price_data[~price_data['stock_name'].str.contains('ST')]
        
        # 剔除上市不足60天的股票
        min_date = price_data.groupby('stock_code')['date'].min().reset_index()
        min_date.columns = ['stock_code', 'min_date']
        price_data = pd.merge(price_data, min_date, on='stock_code')
        price_data = price_data[price_data['date'] >= price_data['min_date'] + timedelta(days=60)]
        
        # 财务数据对齐
        financial_data['quarter'] = financial_data['report_date'].dt.to_period('Q')
        financial_data = financial_data.sort_values(['stock_code', 'report_date'])
        financial_data = financial_data.groupby(['stock_code', 'quarter']).last().reset_index()
        
        return price_data, financial_data
    
    def prepare_factor_data(self, price_data, financial_data):
        """准备因子计算所需数据"""
        # 计算日收益率
        price_data = price_data.sort_values(['stock_code', 'date'])
        price_data['daily_return'] = price_data.groupby('stock_code')['close'].pct_change()
        
        # 计算市场收益率（作为国家因子）
        market_return = price_data.groupby('date')['daily_return'].mean().reset_index()
        market_return.columns = ['date', 'market_return']
        price_data = pd.merge(price_data, market_return, on='date')
        
        # 对齐财务数据（延迟1个月生效）
        price_data['quarter'] = (price_data['date'] - pd.offsets.MonthBegin(1)).dt.to_period('Q')
        price_data = pd.merge(price_data, financial_data, on=['stock_code', 'quarter'], how='left')
        
        # 添加行业信息
        price_data['industry'] = price_data['stock_code'].map(self.industry_mapping)
        
        return price_data

# 因子计算模块
class FactorCalculator:
    def __init__(self):
        self.factor_methods = {
            'BP': self.calculate_bp,
            'EY': self.calculate_ey,
            'BETA': self.calculate_beta,
            'RESVOL': self.calculate_residual_volatility,
            'DY': self.calculate_dy,
            'LTG': self.calculate_ltg,
            'TURN': self.calculate_turnover,
            'LIQ': self.calculate_liquidity,
            'MOM': self.calculate_momentum,
            'LREV': self.calculate_long_term_reversal,
            'EQ': self.calculate_earnings_quality,
            'IQ': self.calculate_investment_quality,
            'PROF': self.calculate_profitability,
            'SIZE': self.calculate_size,
            'MIDCAP': self.calculate_midcap
        }
    
    def calculate_bp(self, data):
        """账面市值比因子"""
        # BP = 账面价值 / 市值
        data['BP'] = data['book_value'] / data['market_cap']
        return data
    
    def calculate_ey(self, data):
        """盈利收益率因子"""
        # EY = 净利润 / 市值
        data['EY'] = data['net_income'] / data['market_cap']
        return data
    
    def calculate_beta(self, data, window=252):
        """贝塔因子"""
        betas = []
        for stock, group in data.groupby('stock_code'):
            if len(group) < window:
                betas.extend([np.nan] * len(group))
                continue
            
            # 计算个股和市场收益率协方差/市场收益率方差
            cov = group['daily_return'].rolling(window).cov(group['market_return'])
            var = group['market_return'].rolling(window).var()
            beta = (cov / var).values
            betas.extend(beta)
        
        data['BETA'] = betas
        return data
    
    def calculate_residual_volatility(self, data, window=63):
        """残差波动率因子"""
        resvol = []
        for stock, group in data.groupby('stock_code'):
            if len(group) < window:
                resvol.extend([np.nan] * len(group))
                continue
            
            # 对市场收益率回归取残差标准差
            X = sm.add_constant(group['market_return'].values)
            y = group['daily_return'].values
            model = LinearRegression().fit(X, y)
            residuals = y - model.predict(X)
            vol = pd.Series(residuals).rolling(window).std().values
            resvol.extend(vol)
        
        data['RESVOL'] = resvol
        return data
    
    def calculate_dy(self, data):
        """股息率因子"""
        # DY = 股息 / 市值
        data['DY'] = data['dividend'] / data['market_cap']
        return data
    
    def calculate_ltg(self, data):
        """长期增长预期因子"""
        # 使用分析师预测的长期增长率
        return data
    
    def calculate_turnover(self, data, window=21):
        """换手率因子"""
        # 21日平均换手率
        data['TURN'] = data['turnover_rate'].rolling(window).mean()
        return data
    
    def calculate_liquidity(self, data, window=21):
        """流动性冲击因子"""
        # 价格变化与成交量的比率
        data['LIQ'] = (data['close'].pct_change() / data['volume']).rolling(window).mean()
        return data
    
    def calculate_momentum(self, data, window=252):
        """12个月动量因子"""
        # 过去12个月收益率（剔除最近1个月）
        data['MOM'] = data.groupby('stock_code')['close'].pct_change(21) / \
                     data.groupby('stock_code')['close'].pct_change(window)
        return data
    
    def calculate_long_term_reversal(self, data, window=504):
        """长期反转因子"""
        # 过去24个月收益率（剔除最近12个月）
        data['LREV'] = data.groupby('stock_code')['close'].pct_change(window) / \
                      data.groupby('stock_code')['close'].pct_change(252)
        return data
    
    def calculate_earnings_quality(self, data):
        """盈利质量因子"""
        # 经营现金流/净利润
        data['EQ'] = data['operating_cash_flow'] / data['net_income']
        return data
    
    def calculate_investment_quality(self, data):
        """投资质量因子"""
        # 资本支出/总资产
        data['IQ'] = data['capital_expenditure'] / data['total_assets']
        return data
    
    def calculate_profitability(self, data):
        """盈利能力因子"""
        # ROE = 净利润/股东权益
        data['PROF'] = data['net_income'] / data['shareholders_equity']
        return data
    
    def calculate_size(self, data):
        """规模因子"""
        # 对数市值
        data['SIZE'] = np.log(data['market_cap'])
        return data
    
    def calculate_midcap(self, data):
        """中盘哑变量"""
        # 市值在中位数附近的股票
        median_cap = data['market_cap'].median()
        data['MIDCAP'] = ((data['market_cap'] > median_cap * 0.5) & 
                         (data['market_cap< median_cap * 2)).astype(int)
        return data
    
    def calculate_all_factors(self, data):
        """计算所有风格因子"""
        for factor, method in self.factor_methods.items():
            data = method(data)
        return data

# 数据处理模块
class DataProcessor:
    def __init__(self):
        self.factor_mean = None
        self.factor_std = None
        
    def handle_missing_values(self, data, factor_cols):
        """处理缺失值"""
        # 行业均值填充
        for factor in factor_cols:
            data[factor] = data.groupby(['date', 'industry'])[factor].transform(
                lambda x: x.fillna(x.mean()))
            
        # 整体均值填充剩余缺失值
        data[factor_cols] = data[factor_cols].fillna(data[factor_cols].mean())
        return data
    
    def winsorize(self, data, factor_cols, n_std=3):
        """极值处理"""
        for factor in factor_cols:
            mean = data[factor].mean()
            std = data[factor].std()
            lower = mean - n_std * std
            upper = mean + n_std * std
            data[factor] = data[factor].clip(lower, upper)
        return data
    
    def standardize(self, data, factor_cols):
        """标准化因子"""
        self.factor_mean = data[factor_cols].mean()
        self.factor_std = data[factor_cols].std()
        data[factor_cols] = (data[factor_cols] - self.factor_mean) / self.factor_std
        return data
    
    def neutralize(self, data, style_factors, industry_dummies):
        """因子中性化"""
        for factor in style_factors:
            X = sm.add_constant(data[industry_dummies])
            y = data[factor]
            model = sm.OLS(y, X).fit()
            data[factor] = model.resid
        return data
    
    def orthogonalize(self, data, factors):
        """因子正交化"""
        # Gram-Schmidt正交化过程
        for i in range(1, len(factors)):
            X = sm.add_constant(data[factors[:i]])
            y = data[factors[i]]
            model = sm.OLS(y, X).fit()
            data[factors[i]] = model.resid
        return data

# 模型构建模块
class BarraModel:
    def __init__(self):
        self.factor_returns = None
        self.factor_cov = None
        self.specific_risk = None
        
    def prepare_factor_exposure(self, data, style_factors, industry_cols):
        """准备因子暴露矩阵"""
        # 国家因子暴露设为1
        data['CNTRY'] = 1
        
        # 合并风格因子和行业因子
        factor_cols = ['CNTRY'] + style_factors + industry_cols
        exposure = data[['date', 'stock_code'] + factor_cols].copy()
        
        # 设置日期为索引
        exposure = exposure.set_index(['date', 'stock_code'])
        return exposure, factor_cols
    
    def calculate_factor_returns(self, exposure, returns, factor_cols):
        """计算因子收益率"""
        factor_returns = []
        
        for date, group in exposure.groupby('date'):
            # 获取当日因子暴露和股票收益率
            X = group[factor_cols]
            y = returns.loc[date].reindex(X.index.get_level_values('stock_code'))
            
            # 剔除缺失值
            valid_idx = ~y.isna() & X.notna().all(axis=1)
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) == 0:
                factor_returns.append(pd.Series(index=factor_cols))
                continue
            
            # 加权最小二乘法（按市值的平方根加权）
            weights = np.sqrt(group.loc[date]['SIZE'].dropna())
            weights = weights.reindex(X.index.get_level_values('stock_code')).fillna(1)
            
            # 约束行业因子收益率之和为0
            industry_cols = [col for col in factor_cols if col.startswith('IND_')]
            if len(industry_cols) > 0:
                X_constraint = X.copy()
                X_constraint['CONSTRAINT'] = X_constraint[industry_cols].sum(axis=1)
                model = sm.WLS(y, X_constraint, weights=weights).fit()
                
                # 调整行业因子收益率
                industry                # 计算行业因子调整量
                industry_sum = model.params[industry_cols].sum()
                adjustment = industry_sum / len(industry_cols)
                
                # 应用调整
                params = model.params.copy()
                params[industry_cols] -= adjustment
                params = params[factor_cols]
            else:
                model = sm.WLS(y, X, weights=weights).fit()
                params = model.params
            
            factor_returns.append(params)
        
        self.factor_returns = pd.DataFrame(factor_returns, index=exposure.index.get_level_values('date').unique())
        return self.factor_returns
    
    def calculate_factor_covariance(self, window=63, lags=5):
        """计算因子协方差矩阵（Newey-West调整）"""
        if self.factor_returns is None:
            raise ValueError("需要先计算因子收益率")
            
        dates = self.factor_returns.index
        factor_cov = {}
        
        for i in range(window, len(dates)):
            current_date = dates[i]
            returns = self.factor_returns.iloc[i-window:i]
            
            # 计算样本协方差
            cov = returns.cov()
            
            # Newey-West调整
            for lag in range(1, lags+1):
                autocov = returns.shift(lag).cov(returns)
                weight = 1 - lag/(lags+1)
                cov += weight * (autocov + autocov.T)
            
            factor_cov[current_date] = cov
        
        self.factor_cov = pd.concat(factor_cov, axis=0)
        return self.factor_cov
    
    def calculate_specific_risk(self, exposure, returns):
        """计算特质风险"""
        specific_risk = {}
        
        for date, group in exposure.groupby('date'):
            # 获取当日因子暴露和股票收益率
            X = group
            y = returns.loc[date].reindex(X.index.get_level_values('stock_code'))
            
            # 剔除缺失值
            valid_idx = ~y.isna() & X.notna().all(axis=1)
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) == 0:
                continue
            
            # 计算残差
            factor_ret = self.factor_returns.loc[date]
            pred_return = (X * factor_ret).sum(axis=1)
            residual = y - pred_return
            
            # 计算残差波动率（21天滚动）
            residual_df = pd.DataFrame({'residual': residual, 'stock_code': X.index.get_level_values('stock_code')})
            residual_df = residual_df.set_index('stock_code', append=True)
            
            if date not in specific_risk:
                specific_risk[date] = {}
            
            for stock in residual_df.index.get_level_values('stock_code').unique():
                stock_resid = residual_df.xs(stock, level='stock_code')['residual']
                if len(stock_resid) >= 21:
                    specific_risk[date][stock] = stock_resid.rolling(21).std().iloc[-1]
                else:
                    specific_risk[date][stock] = np.nan
        
        self.specific_risk = pd.DataFrame.from_dict(specific_risk, orient='index')
        return self.specific_risk
    
    def predict_risk(self, exposure, date):
        """风险预测"""
        if date not in self.factor_cov.index.get_level_values(0):
            raise ValueError(f"没有找到日期 {date} 的因子协方差矩阵")
            
        # 获取特定日期的因子协方差
        factor_cov = self.factor_cov.xs(date, level=0)
        
        # 个股风险预测
        stock_risk = {}
        for stock, row in exposure.loc[date].iterrows():
            if stock in self.specific_risk.columns and pd.notna(self.specific_risk.loc[date, stock]):
                factor_risk = np.sqrt(row @ factor_cov @ row.T)
                specific_risk = self.specific_risk.loc[date, stock]
                total_risk = np.sqrt(factor_risk**2 + specific_risk**2)
                stock_risk[stock] = total_risk
        
        return pd.Series(stock_risk)

# 报告生成模块
class ReportGenerator:
    def __init__(self, model):
        self.model = model
    
    def plot_factor_returns(self):
        """绘制因子收益率时序图"""
        plt.figure(figsize=(15, 8))
        for factor in self.model.factor_returns.columns:
            plt.plot(self.model            plt.plot(self.model.factor_returns[factor], label=factor)
        plt.title('Factor Returns Over Time')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid()
        plt.show()
    
    def plot_factor_correlation(self, date):
        """绘制因子相关性热力图"""
        if date not in self.model.factor_cov.index.get_level_values(0):
            raise ValueError(f"没有找到日期 {date} 的因子协方差矩阵")
            
        factor_corr = self.model.factor_cov.xs(date, level=0).copy()
        np.fill_diagonal(factor_corr.values, 1)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(factor_corr, annot=True, fmt=".2f", cmap='coolwarm', 
                   center=0, vmin=-1, vmax=1)
        plt.title(f'Factor Correlation Matrix ({date})')
        plt.show()
    
    def generate_risk_report(self, portfolio_weights, date):
        """生成风险归因报告"""
        if date not in self.model.factor_cov.index.get_level_values(0):
            raise ValueError(f"没有找到日期 {date} 的因子协方差矩阵")
            
        # 计算组合因子暴露
        portfolio_exposure = portfolio_weights @ self.model.exposure.loc[date]
        
        # 计算风险贡献
        factor_cov = self.model.factor_cov.xs(date, level=0)
        marginal_risk = factor_cov @ portfolio_exposure
        risk_contribution = portfolio_exposure * marginal_risk
        
        # 计算风险占比
        total_risk = np.sqrt(portfolio_exposure @ factor_cov @ portfolio_exposure.T)
        risk_pct = risk_contribution / total_risk**2
        
        # 生成报告
        report = pd.DataFrame({
            'Factor': risk_pct.index,
            'Exposure': portfolio_exposure.values,
            'Risk Contribution': risk_contribution.values,
            'Risk Percentage': risk_pct.values
        }).sort_values('Risk Percentage', ascending=False)
        
        return report

# 主程序
def main():
    # 1. 数据准备
    print("Step 1: 数据准备...")
    preprocessor = DataPreprocessor()
    price_data = preprocessor.load_price_data('data/price_data.csv')
    financial_data = preprocessor.load_financial_data('data/financial_data.csv')
    industry_data = preprocessor.load_industry_data('data/industry_data.csv')
    price_data, financial_data = preprocessor.clean_data(price_data, financial_data)
    factor_data = preprocessor.prepare_factor_data(price_data, financial_data)
    
    # 创建行业哑变量
    industry_dummies = pd.get_dummies(factor_data['industry'], prefix='IND')
    factor_data = pd.concat([factor_data, industry_dummies], axis=1)
    industry_cols = industry_dummies.columns.tolist()
    
    # 2. 因子计算
    print("Step 2: 因子计算...")
    calculator = FactorCalculator()
    factor_data = calculator.calculate_all_factors(factor_data)
    style_factors = list(calculator.factor_methods.keys())
    
    # 3. 数据处理
    print("Step 3: 数据处理...")
    processor = DataProcessor()
    factor_data = processor.handle_missing_values(factor_data, style_factors)
    factor_data = processor.winsorize(factor_data, style_factors)
    factor_data = processor.standardize(factor_data, style_factors)
    factor_data = processor.neutralize(factor_data, style_factors, industry_cols)
    factor_data = processor.orthogonalize(factor_data, style_factors)
    
    # 4. 模型构建
    print("Step 4: 模型构建...")
    barra_model = BarraModel()
    
    # 准备因子暴露矩阵
    exposure, factor_cols = barra_model.prepare_factor_exposure(
        factor_data, style_factors, industry_cols)
    
    # 准备股票收益率数据
    returns = factor_data.groupby(['date', 'stock_code'])['daily_return'].last().unstack()
    
    # 计算因子收益率
    factor_returns = barra_model.calculate_factor_returns(exposure, returns, factor_cols)
    
    # 计算因子协方差矩阵
    factor_cov = barra_model.calculate_factor_covariance()
    
    # 计算特质风险
    specific_risk = barra_model.calculate_specific    specific_risk = barra_model.calculate_specific_risk(exposure, returns)
    
    # 5. 风险预测示例
    print("Step 5: 风险预测...")
    test_date = '2023-12-31'
    if test_date in exposure.index.get_level_values('date'):
        risk_prediction = barra_model.predict_risk(exposure, test_date)
        print(f"\n个股风险预测 (日期: {test_date}):")
        print(risk_prediction.head())
    else:
        print(f"警告: 测试日期 {test_date} 无可用数据")
    
    # 6. 生成报告
    print("\nStep 6: 生成分析报告...")
    reporter = ReportGenerator(barra_model)
    
    # 绘制因子收益率时序图
    print("\n生成因子收益率时序图...")
    reporter.plot_factor_returns()
    
    # 绘制因子相关性热力图
    if test_date in factor_cov.index.get_level_values(0):
        print(f"\n生成因子相关性热力图 (日期: {test_date})...")
        reporter.plot_factor_correlation(test_date)
    
    # 生成风险归因报告示例
    if test_date in exposure.index.get_level_values('date'):
        print(f"\n生成风险归因报告 (日期: {test_date})...")
        # 创建示例组合 (等权重)
        stocks_on_date = exposure.loc[test_date].index.get_level_values('stock_code')
        weights = pd.Series(1/len(stocks_on_date), index=stocks_on_date)
        risk_report = reporter.generate_risk_report(weights, test_date)
        print("\n风险归因报告:")
        print(risk_report)
    
    print("\nBARRA CNE6 模型构建完成!")

if __name__ == "__main__":
    main()

TERMINATE
                
        