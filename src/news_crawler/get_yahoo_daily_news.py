import requests
import pandas as pd
import twstock
from bs4 import BeautifulSoup
from datetime import timedelta
# from fake_useragent import UserAgent
from src.financial_crawler.fetch_daily_exchange import get_stock_list

twstock.__update_codes()

CONFUSED_LIST = [['聯發科', '聯發'], ['華新', '華新科'], ['台塑化', '台塑'], ['南亞科', '南亞']]

def get_yahoo_news(stock_code: str, date: str):
    # Get the news of a specific stock from Yahoo Finance
    # 每週一爬 爬過去一週 （週二～週一晚上）
    df_stocks = get_stock_list(date)
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
    df_yahoo_news = []
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
            df_yahoo_news.append({
                'stat_date': pd.to_datetime(datetime_.date()),
                '標題': title,
                '時間': datetime_,
                '關鍵字': ','.join(keywords),
                '內容': news_content
            })
        except:
            pass
    df_yahoo_news = pd.DataFrame(df_yahoo_news)
    df_yahoo_news = df_yahoo_news[
        (df_yahoo_news.stat_date > pd.to_datetime(date) - timedelta(days=7)) \
        & (df_yahoo_news.stat_date <= pd.to_datetime(date))
    ].copy()
    if len(df_yahoo_news) > 0:
        return df_yahoo_news
    else:
        return f"{date}未爬到任何新聞"
