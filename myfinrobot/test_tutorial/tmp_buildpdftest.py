import os
import matplotlib.pyplot as plt
import numpy as np
from myfinrobot.functional.reportlab import ReportLabUtils

def generate_temp_images():
    """生成临时图像文件用于测试"""
    # 创建临时目录
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成股价走势图
    plt.figure(figsize=(8, 4))
    x = np.arange(0, 10, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.title("股价走势")
    share_path = os.path.join(temp_dir, "share_performance.png")
    plt.savefig(share_path)
    plt.close()
    
    # 生成PE/EPS走势图
    plt.figure(figsize=(8, 4))
    plt.plot(x, y * 2, label="PE")
    plt.plot(x, y * 0.5, label="EPS")
    plt.legend()
    plt.title("PE/EPS走势")
    pe_eps_path = os.path.join(temp_dir, "pe_eps_performance.png")
    plt.savefig(pe_eps_path)
    plt.close()
    
    return share_path, pe_eps_path

if __name__ == "__main__":
    # 生成临时图像
    share_img, pe_eps_img = generate_temp_images()
    
    # 创建报告目录
    report_dir = "testreport"
    os.makedirs(report_dir, exist_ok=True)
    
    # 调用报告生成函数
    result = ReportLabUtils.build_annual_report_cn(
        ticker_symbol="AAPL",
        save_path=report_dir,
        operating_results="苹果公司过去一年表现强劲，收入增长显著。",
        market_position="苹果是全球领先的科技公司，在智能手机市场占据主导地位。",
        business_overview="苹果公司设计、生产和销售消费电子产品、计算机软件和在线服务。",
        risk_assessment='{"风险1": "全球经济衰退可能影响消费者支出", "风险2": "汇率波动可能影响海外收入"}',
        competitors_analysis='{"三星": "主要竞争对手，在智能手机市场有强大份额", "华为": "在中国市场增长迅速"}',
        share_performance_image_path=share_img,
        pe_eps_performance_image_path=pe_eps_img,
        filing_date="2023-12-31"
    )
    
    print("报告生成结果:", result)
    print(f"报告保存在: {os.path.abspath(report_dir)}")