import time
import html
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime, date, timedelta
from utils.utils import upload_data_to_mysql


retry_strategy = Retry(
    total=5,
    backoff_factor=0.2, 
    status_forcelist=[500, 502, 503, 504, 404],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
HTTP = requests.Session()
HTTP.mount("https://", adapter)
HTTP.mount("http://", adapter)

def date_to_timestamp(_date: str):
    date_start = _date + ' 00:00:00'
    date_end = _date + ' 23:59:59'
    ts_start= int(time.mktime(datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S").timetuple()))
    ts_end= int(time.mktime(datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S").timetuple()))
    return ts_start, ts_end

def content_html_decoder(text):
    decoded_text = html.unescape(text)
    soup = BeautifulSoup(decoded_text, 'html.parser')
    formatted_text = soup.get_text('\n', strip=True)  # 每個段落用換行分隔
    return formatted_text

def get_news_dict_list(json_data):
    # Extract data from JSON and construct a list of dictionaries
    return [
        {
            '標題': item['title'],
            '時間': pd.to_datetime(item['publishAt'], unit='s'),
            '關鍵字': ','.join(item['keyword']),
            '內容': content_html_decoder(item['content'])
        }
        for item in json_data['items']['data']
    ]

def get_anue_news(_date: str):
    ts_start, ts_end = date_to_timestamp(_date)
    page = 1
    url_template = "https://api.cnyes.com/media/api/v1/newslist/category/tw_stock_news?page={page}&limit=30&startAt={ts_start}&endAt={ts_end}"
    url = url_template.format(page=page, ts_start=ts_start, ts_end=ts_end)
    response = HTTP.get(url)
    response.raise_for_status()
    json_data = json.loads(response.text)
    n_news = json_data['items']['total']
    last_page = json_data['items']['last_page']
    if n_news > 0:
        news_list = get_news_dict_list(json_data)
    else:
        return f"{_date}未爬到任何新聞"
    if last_page > 1:
        for page in range(2, last_page + 1):
            url = url_template.format(page=page, ts_start=ts_start, ts_end=ts_end)
            response = HTTP.get(url)
            response.raise_for_status()
            json_data = json.loads(response.text)
            news_list.extend(get_news_dict_list(json_data))
    df = pd.DataFrame(news_list)
    df.insert(0, 'stat_date', pd.to_datetime(_date))
    return df


if __name__ == '__main__':
    TODAY = date.today()
    YESTERDAY = TODAY - timedelta(days=1)
    yesterday_str = YESTERDAY.strftime('%Y-%m-%d')

    print("========== Anue新聞 ==========")
    df_anue_news = get_anue_news(yesterday_str)
    if isinstance(df_anue_news, pd.DataFrame):
        upload_data_to_mysql(df_anue_news, 'daily_news_crawl')
    else:
        print(df_anue_news)
    print("========== DONE ==========")
