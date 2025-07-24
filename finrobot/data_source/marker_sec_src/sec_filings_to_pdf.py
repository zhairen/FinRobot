from typing import List
import re
import pandas as pd
from datetime import datetime
from typing import Union, Final
import requests
import pdfkit
import os
import json

SEC_SEARCH_URL: Final[str] = "http://www.sec.gov/cgi-bin/browse-edgar"


def _search_url(cik: Union[str, int]) -> str:
    search_string = f"CIK={cik}&Find=Search&owner=exclude&action=getcompany"
    url = f"{SEC_SEARCH_URL}?{search_string}"
    return url


def get_cik_by_ticker(ticker: str) -> str:
    """Gets a CIK number from a stock ticker by running a search on the SEC website."""
    cik_re = re.compile(r".*CIK=(\d{10}).*")
    url = _search_url(ticker)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    company = "Indiana-University-Bloomington"
    email = "athecolab@gmail.com"
    headers = {
        "User-Agent": f"{company} {email}",
        "Content-Type": "text/html",
    }
    print(f"[INFO] 正在获取股票代码 {ticker} 的CIK... 请求URL: {url}")
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()
    results = cik_re.findall(response.text)
    print(f"[INFO] 获取到CIK: {results[0]}（股票代码: {ticker}）")
    return str(results[0])


SEC_EDGAR_URL = "https://www.sec.gov/Archives/edgar/data"

BASE_DIR = "output/SEC_EDGAR_FILINGS"
os.makedirs(BASE_DIR, exist_ok=True)


def sec_save_pdfs(
    ticker: str,
    year: str,
    filing_types: List[str] = ["10-K", "10-Q"],
    include_amends=True,
):
    # 新增：关键节点输出 - 开始处理
    print(f"\n[PROCESS] 开始处理股票 {ticker} {year} 年的SEC文件下载...")
    print(f"[CONFIG] 配置参数 -  filings_types: {filing_types}, include_amends: {include_amends}")

    # 获取CIK（新增输出）
    cik = get_cik_by_ticker(ticker)
    rgld_cik = int(cik.lstrip("0"))
    ticker_year_path = os.path.join(BASE_DIR, f"{ticker}-{year}")
    os.makedirs(ticker_year_path, exist_ok=True)
    print(f"[INFO] 输出目录已创建: {ticker_year_path}")

    # 构造文件类型列表（新增输出）
    forms = []
    if include_amends:
        for ft in filing_types:
            forms.append(ft)
            forms.append(ft + "/A")
    print(f"[INFO] 待筛选的文件类型: {forms}")

    # 请求公司提交记录（新增输出）
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(f"[REQUEST] 正在请求公司提交记录... URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"[SUCCESS] 公司提交记录请求成功（状态码: {response.status_code}）")
        json_data = response.json()
    else:
        print(f"[ERROR] 公司提交记录请求失败（状态码: {response.status_code}）")
        return [], {}, "", ""

    # 筛选符合条件的文件（新增输出）
    filings = json_data["filings"]
    recent_filings = filings["recent"]
    form_lists = []
    sec_form_names = []
    for acc_num, form_name, filing_date, report_date in zip(
        recent_filings["accessionNumber"],
        recent_filings["form"],
        recent_filings["filingDate"],
        recent_filings["reportDate"],
    ):
        if form_name in forms and report_date.startswith(str(year)):
            # 处理10-Q季度标识（新增输出）
            if form_name == "10-Q":
                datetime_obj = datetime.strptime(report_date, "%Y-%m-%d")
                quarter = pd.Timestamp(datetime_obj).quarter
                form_name += str(quarter)
                if form_name in sec_form_names:
                    form_name += "-1"
                print(f"[INFO] 检测到10-Q文件，标记季度为Q{quarter}（调整后文件名: {form_name}）")
            no_dashes_acc_num = re.sub("-", "", acc_num)
            form_lists.append([no_dashes_acc_num, form_name, filing_date, report_date])
            sec_form_names.append(form_name)
    print(f"[INFO] 筛选出符合条件的文件: {len(form_lists)} 个（年份: {year}）")

    # 生成HTML链接（新增输出）
    process_links = lambda x: "".join(x.split("-"))
    acc_nums_list = [[fl[0], fl[1], process_links(fl[-1])] for fl in form_lists]
    html_urls = [
        [
            f"{SEC_EDGAR_URL}/{rgld_cik}/{acc}/{ticker.lower()}-{report_date}.htm",
            filing_type,
        ]
        for acc, filing_type, report_date in acc_nums_list
    ]
    print(f"[INFO] 生成HTML下载链接: {len(html_urls)} 个")

    # 转换HTML到PDF（新增输出）
    print(f"\n[PROCESS] 开始转换HTML到PDF（共 {len(html_urls)} 个文件）...")
    metadata_json = _convert_html_to_pdfs(html_urls, ticker_year_path)
    print(f"[SUCCESS] PDF转换完成！生成文件数: {len(metadata_json)}")

    # 保存元数据（新增输出）
    metadata_file_path = os.path.join(ticker_year_path,'metadata.json') 
    with open(metadata_file_path, 'w') as f:
        json.dump(metadata_json, f)
    print(f"[INFO] 元数据已保存至: {metadata_file_path}")

    return html_urls, metadata_json, metadata_file_path,ticker_year_path


def _convert_html_to_pdfs(html_urls, base_path: str):
    metadata_json = {}
    for idx, html_url in enumerate(html_urls, 1):
        # 新增：单个文件转换输出
        print(f"[CONVERT] 处理第 {idx}/{len(html_urls)} 个文件... URL: {html_url[0]}")
        pdf_path = html_url[0].split("/")[-1]
        pdf_path = pdf_path.replace(".htm", f"-{html_url[1]}.pdf")
        pdf_path = pdf_path.replace("10-K/A", "10-KA")  # 处理修正文件路径问题
        full_pdf_path = os.path.join(base_path, pdf_path)
        metadata_json[pdf_path] = {"languages": ["English"]}
        # 新增：转换状态输出
        try:
            pdfkit.from_url(html_url[0], full_pdf_path)
            print(f"[SUCCESS] PDF保存成功: {full_pdf_path}")
        except Exception as e:
            print(f"[ERROR] PDF转换失败（URL: {html_url[0]}）: {str(e)}")
    return metadata_json
