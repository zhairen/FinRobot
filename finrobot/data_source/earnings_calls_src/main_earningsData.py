from earnings_calls_src.earningsData import get_earnings_transcript
import re
from langchain.schema import Document
from tenacity import RetryError


def clean_speakers(speaker):
    speaker = re.sub("\n", "", speaker)
    speaker = re.sub(":", "", speaker)
    return speaker


def get_earnings_all_quarters_data(quarter: str, ticker: str, year: int):
    print(f'[DEBUG] 开始处理季度数据 quarter={quarter}, ticker={ticker}, year={year}')
    
    if not all([quarter, ticker, year]):
        print('[ERROR] 缺少必要参数')
        return [], []

    try:
        print(f'[API REQUEST] 请求财报电话数据...')
        resp_dict = get_earnings_transcript(quarter, ticker, year)
        print(f'[API RESPONSE] 响应状态: {resp_dict.get("status", "unknown")}')

        # 新增：直接使用earningsData返回的transcript_split结构化数据
        transcript_split = resp_dict.get("transcript_split", [])
        if not transcript_split:
            print('[WARNING] 未获取到transcript_split数据')
            return [], []

        # 初始化docs和speakers_list
        docs = []
        speakers_list = []

        # 遍历transcript_split生成docs和speakers_list
        for item in transcript_split:
            speaker = item.get("speaker", "未知发言人")
            text = item.get("text", "")
            # 清洗发言人名称（与原有clean_speakers逻辑一致）
            cleaned_speaker = clean_speakers(speaker)
            speakers_list.append(cleaned_speaker)

            # 构建Document对象（metadata包含speaker和quarter）
            docs.append(
                Document(
                    page_content=text,
                    metadata={"speaker": cleaned_speaker, "quarter": quarter}
                )
            )

        print(f'[DATA] 成功生成{len(docs)}条发言人对话记录')
        return docs, speakers_list

    except Exception as e:
        print(f'[ERROR] 请求处理失败: {e}')
        return [], []    


def get_earnings_all_docs(ticker: str, year: int):
    earnings_docs = []
    earnings_call_quarter_vals = []
    print("Earnings Call Q1")
    try:
        docs, speakers_list_1 = get_earnings_all_quarters_data("Q1", ticker, year)
        earnings_call_quarter_vals.append("Q1")
        earnings_docs.extend(docs)
    except RetryError:
        print(f"Don't have the data for Q1")
        speakers_list_1 = []

    print("Earnings Call Q2")
    try:
        docs, speakers_list_2 = get_earnings_all_quarters_data("Q2", ticker, year)
        earnings_call_quarter_vals.append("Q2")
        earnings_docs.extend(docs)
    except RetryError:
        print(f"Don't have the data for Q2")
        speakers_list_2 = []
    print("Earnings Call Q3")
    try:
        docs, speakers_list_3 = get_earnings_all_quarters_data("Q3", ticker, year)
        earnings_call_quarter_vals.append("Q3")
        earnings_docs.extend(docs)
    except RetryError:
        print(f"Don't have the data for Q3")
        speakers_list_3 = []
    print("Earnings Call Q4")
    try:
        docs, speakers_list_4 = get_earnings_all_quarters_data("Q4", ticker, year)
        earnings_call_quarter_vals.append("Q4")
        earnings_docs.extend(docs)
    except RetryError:
        print(f"Don't have the data for Q4")
        speakers_list_4 = []
    return (
        earnings_docs,
        earnings_call_quarter_vals,
        speakers_list_1,
        speakers_list_2,
        speakers_list_3,
        speakers_list_4,
    )
