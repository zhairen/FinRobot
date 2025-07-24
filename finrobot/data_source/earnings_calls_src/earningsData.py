from tenacity import retry, stop_after_attempt, wait_random_exponential
import requests
import json
from datetime import datetime
import re
from typing import List, Dict


def correct_date(yr, dt):
    """Some transcripts have incorrect date, correcting it（未修改）"""
    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    if dt.year != yr:
        dt = dt.replace(year=yr)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_speakers(cont: str) -> List[str]:
    """Extract the list of speakers（未修改）"""
    pattern = re.compile(r"\n(.*?):")
    matches = pattern.findall(cont)
    return list(set(matches))


MYCALLKEY = "EqFQb7cumnrL5yRtQQeLwQ==B208UJotA6PcRhap"


@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(2))
def get_earnings_transcript(quarter: str, ticker: str, year: int) -> Dict:
    """获取财报电话记录（适配main函数所需的返回结构）"""
    print(ticker,year,quarter)
    quarter = quarter.replace("Q","")
    
    api_url = 'https://api.api-ninjas.com/v1/earningstranscript?ticker={}&year={}&quarter={}'.format(ticker, year, quarter)
    resp_data = {}  # 初始化返回字典

    try:
        response = requests.get(
            api_url,
            headers={'X-Api-Key': MYCALLKEY},
            timeout=30
        )
        # 新增：设置status字段（main函数需要）
        resp_data["status"] = "success" if response.status_code == 200 else "error"

        if response.status_code != 200:
            print(f'[ERROR] API请求失败，状态码: {response.status_code}')
            return resp_data  # 包含status的空字典

        resp_json = json.loads(response.text)
        # 关键修改：将transcript重命名为content（main函数需要访问content字段）
        resp_data["content"] = resp_json.get("transcript", "")
        # 保留其他原始字段
        resp_data.update({
            "date": resp_json.get("date", ""),
            "transcript_split": resp_json.get("transcript_split", []),
            "ticker": resp_json.get("ticker", ""),
            "year": resp_json.get("year", ""),
            "quarter": resp_json.get("quarter", ""),
        })

        # 修正日期格式（逻辑不变）
        full_date = f"{resp_data['date']} 00:00:00"
        corrected_date = correct_date(int(resp_data['year']), full_date)
        resp_data['date'] = corrected_date

        # 保留计算字段（transcript_length重命名为content_length）
        resp_data["content_length"] = len(resp_data["content"])
        # 计算发言人最大文本长度（逻辑不变）
        speaker_text_lengths: Dict[str, int] = {}
        for item in resp_data.get("transcript_split", []):
            speaker = item.get("speaker", "未知发言人")
            text = item.get("text", "")
            current_length = len(text)
            if speaker not in speaker_text_lengths or current_length > speaker_text_lengths[speaker]:
                speaker_text_lengths[speaker] = current_length
        resp_data["max_speaker_text_length"] = speaker_text_lengths

        return resp_data

    except json.JSONDecodeError:
        resp_data["status"] = "error"
        print('[ERROR] 响应内容非JSON格式')
        return resp_data
    except Exception as e:
        resp_data["status"] = "error"
        print(f'[ERROR] 通用异常: {str(e)}')
        return resp_data


if __name__ == "__main__":
    # 测试参数（可修改为实际需要的股票、年份、季度）
    import requests

    ticker = 'MSFT'
    year = 2024
    quarter = 2

    api_url = 'https://api.api-ninjas.com/v1/earningstranscript?ticker={}&year={}&quarter={}'.format(ticker, year, quarter)
    response = requests.get(api_url, headers={'X-Api-Key': MYCALLKEY}, timeout=30)
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)