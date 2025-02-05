import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

import requests
import pandas as pd
import twstock
from bs4 import BeautifulSoup
from datetime import timedelta, date

# from fake_useragent import UserAgent
from utils.db_funcs import upload_data_to_mysql
from financial_crawler.fetch_daily_exchange import get_stock_list


CONFUSED_LIST = [['聯發科', '聯發'], ['華新', '華新科'], ['台塑化', '台塑'], ['南亞科', '南亞']]

def get_yahoo_news(stock_code: str, date_: str):
    # Get the news of a specific stock from Yahoo Finance
    # 每週一爬 爬過去一週 （週二～週一晚上）
    df_stocks = get_stock_list(date_)
    stock_list = (
            df_stocks['證券代號'].tolist() + df_stocks['證券名稱'].tolist()
    )
    stock_name = twstock.codes[stock_code].name
    exclude_stock = None
    for pair in CONFUSED_LIST:
        if stock_name in pair:
            pair.remove(stock_name)
            exclude_stock = pair[0]
            break
    formatted_url = 'https://tw.stock.yahoo.com/quote/{}.TW/news'
    url = formatted_url.format(stock_code)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    # UserAgent().random
    headers = {
        'User-Agent': user_agent
    }
    response = requests.get(url, headers=headers, timeout=10)
    assert response.status_code == 200, "get url false"
    page_content = BeautifulSoup(response.content, 'html.parser')
    news_items = page_content.find_all('li', class_='js-stream-content Pos(r)')
    df_news = []
    for item in news_items:
        try:
            title = item.find('h3').get_text()
            href_page = requests.get(item.find('a')['href'], timeout=10)
            assert href_page.status_code == 200, "get url false"
            href_page_resp = BeautifulSoup(href_page.content, 'html.parser')
            news_content = href_page_resp.find('div', {'class': 'caas-body'}).get_text()
            datetime_ = pd.to_datetime(href_page_resp.find('time', {'class': 'caas-attr-meta-time'})['datetime'])
            keywords = [kw for kw in stock_list if kw in news_content]
            if exclude_stock:
                keywords.remove(exclude_stock)
            df_news.append({
                'stat_date': pd.to_datetime(datetime_.date()),
                '標題': title,
                '時間': datetime_,
                '關鍵字': ','.join(keywords),
                '內容': news_content
            })
        except:
            pass
    df_news = pd.DataFrame(df_news)
    df_news = df_news[
        (df_news.stat_date > pd.to_datetime(date_) - timedelta(days=7)) \
        & (df_news.stat_date <= pd.to_datetime(date_))
    ].copy()
    if len(df_news) > 0:
        return df_news
    else:
        return f"{date_}未爬到任何新聞"

EXCLUDE_FIELDS = [
    '水泥工業', '食品工業', '塑膠工業', '其他業', '紡織纖維', '運動休閒', '玻璃陶瓷',
    '居家生活', '橡膠工業', '電子通路業', '資訊服務業', '貿易百貨業', '數位雲端'
]

if __name__ == '__main__':
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    today_str = date.today().strftime('%Y%m%d')
    weekday = date.today().weekday()
    if weekday == 0:
        # Every Monday
        print("========== Yahoo新聞 ==========")
        # get stock tick list
        df_stocks = get_stock_list(today_str)
        stock_list = df_stocks.loc[
            (df_stocks['類型'] == '股票') \
            & ~(df_stocks['產業'].isin(EXCLUDE_FIELDS)),
        '證券代號'].tolist()

        df_yahoo_news = []
        for stock in stock_list:
            try:
                temp = get_yahoo_news(stock_list[0], yesterday_str)
                if isinstance(temp, pd.DataFrame):
                    df_yahoo_news.append(temp)
            except:
                print(f"Fetch Yahoo news failed for {stock}")
                pass
        df_yahoo_news = pd.concat(df_yahoo_news)
        if isinstance(df_yahoo_news, pd.DataFrame):
            upload_data_to_mysql(df_yahoo_news, 'daily_news_crawl')
        else:
            print(df_yahoo_news)
        print("========== DONE ==========")
    else:
        sys.exit(0)