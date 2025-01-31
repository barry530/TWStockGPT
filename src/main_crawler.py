import os
import traceback
from pathlib import Path
from ast import literal_eval
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine

from financial_crawler.fetch_financial_report import fetch_monthly_revenue, fetch_seasonal_report
from financial_crawler.process_monthly_revenue import process_monthly_revenue
from financial_crawler.process_comprehensive_income import process_comprehensive_income
from financial_crawler.process_cash_flow import process_cash_flow
from financial_crawler.process_balance_sheet import process_balance_sheet
from financial_crawler.fetch_daily_exchange import get_daily_exchange_info, get_stock_list
from news_crawler.get_anue_daily_news import get_anue_news
from news_crawler.get_yahoo_daily_news import get_yahoo_news

TEMP_PATH = Path('./data/temp')  # GitHub path
DB_CONNECTION = literal_eval(os.environ['DB_CONNECTION'])
HOST = DB_CONNECTION['host']
PORT = DB_CONNECTION['port']
USERNAME = DB_CONNECTION['username']
PASSWORD = DB_CONNECTION['password']
DATABASE = DB_CONNECTION['database']
print(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
# ENGINE = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')

EXCLUDE_FIELDS = [
    '水泥工業', '食品工業', '塑膠工業', '其他業', '紡織纖維', '運動休閒', '玻璃陶瓷',
    '居家生活', '橡膠工業', '電子通路業', '資訊服務業', '貿易百貨業', '數位雲端'
]


if __name__ == '__main__':
    # 每日交易：每個工作天
    # 月報：下個月12
    # 季報：下一季第一天
    TODAY = date.today()
    YESTERDAY = TODAY - timedelta(days=1)
    YEAR = TODAY.year
    MONTH = TODAY.month
    DAY = TODAY.day
    today_str = '20250117'  # TODAY.strftime('%Y%m%d')
    yesterday_str = '2025-01-16'  # YESTERDAY.strftime('%Y-%m-%d')

    df_stocks = get_stock_list(today_str)
    print("========== 股票清單 ==========", df_stocks)
    df_anue_news = get_anue_news(yesterday_str)
    print("========== Anue新聞 ==========", df_anue_news)
    df_yahoo_news = get_yahoo_news(2330, yesterday_str)
    print("========== Yahoo新聞 ==========", df_yahoo_news)
    df_daily_exchange_info = get_daily_exchange_info(today_str)
    print("========== 每日成交資訊 ==========", df_daily_exchange_info)
    fetch_monthly_revenue(2024, 12)
    df_monthly_rev = process_monthly_revenue(2024, 12)
    print("========== 月營收 ==========", df_monthly_rev)
    for market_type in ['上市', '上櫃']:
        for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
            fetch_seasonal_report(2024, 3, market_type, report_type)
    df_comprehensive_income = process_comprehensive_income(2024, 3)
    print("========== 綜合損益表 ==========", df_comprehensive_income)
    df_cash_flow = process_cash_flow(2024, 3)
    print("========== 現金流量表 ==========", df_cash_flow)
    df_balance_sheet = process_balance_sheet(2024, 3)
    print("========== 資產負債表 ==========", df_balance_sheet)

    print("EXIT", ENGINE)

    print("========== Anue新聞 ==========")
    df_anue_news = get_anue_news(yesterday_str)
    if isinstance(df_anue_news, pd.DataFrame):
        df_anue_news.to_sql(
            'daily_news_crawl',
            con=ENGINE,
            if_exists='append',
            index=False
        )
    else:
        print(df_anue_news)

    if TODAY.weekday() == 0:  # Monday(0) 每週一爬Yahoo新聞
        print("========== Yahoo新聞 ==========")
        stock_list = df_stocks.loc[
            (df_stocks['類型'] == '股票') \
            & ~(df_stocks['產業'].isin(EXCLUDE_FIELDS)), '證券代號'
        ].tolist()
        df_yahoo_news = []
        for stock in stock_list:
            try:
                temp = get_yahoo_news(stock_list[0], yesterday_str)
                if isinstance(temp, pd.DataFrame):
                    df_yahoo_news.append(temp)
            except:
                print(f"Fetch Yahoo news failed for {stock}")
                traceback.print_exc()
        df_yahoo_news = pd.concat(df_yahoo_news)
        if len(df_yahoo_news) > 0:
            df_yahoo_news.to_sql(
                'daily_news_crawl',
                con=ENGINE,
                if_exists='append',
                index=False
            )
        else:
            print("No Yahoo news")

    print("========== 每日成交資訊 ==========")
    if TODAY.weekday() < 5:  # Monday(0) to Friday(4)
        df_daily_exchange_info = get_daily_exchange_info(today_str)
        print(df_daily_exchange_info)
        if len(df_daily_exchange_info) > 0:
            file_name = f"{today_str}成交資訊.csv"
            df_daily_exchange_info.to_sql(
                'daily_exchange_info',
                con=ENGINE,
                if_exists='append',
                index=False
            )
        else:
            print(f"{today_str}無成交資訊")
        print("========== DONE ==========")

    print("========== 月營收 ==========")
    if DAY == 12:  # 次月的10日之前，抓12
        if MONTH == 1:  # 拿去年12月
            fetch_year = YEAR - 1
            fetch_month = 12
        else:
            fetch_year = YEAR
            fetch_month = MONTH-1
        fetch_monthly_revenue(fetch_year, fetch_month)
        df_monthly_rev = process_monthly_revenue(fetch_year, fetch_month)
        if isinstance(df_monthly_rev, pd.DataFrame):
            df_monthly_rev.to_sql(
                'monthly_revenue',
                con=ENGINE,
                if_exists='append',
                index=False
            )
        else:
            print(df_monthly_rev)
        print("========== DONE ==========")

    if MONTH in [6, 9, 12, 4] and DAY == 1:
        # 第一季：5月15日前
        # 第二季：8月14日前
        # 第三季：11月14日前
        # 第四季：3月15日前，其餘應在4月1日前
        # 但金融股、KY股不在此限，在月底前公布即可

        print('========== 財務報表 ==========')
        for market_type in ['上市', '上櫃']:
            for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
                print(f"{market_type} {report_type}")
                if MONTH == 4:  # 拿去年第四季
                    fetch_season = 4
                    fetch_year = YEAR - 1
                else:
                    fetch_season = MONTH // 3 - 1  # 拿上季報表
                    fetch_year = YEAR
                fetch_seasonal_report(fetch_year, fetch_season, market_type, report_type)

        print('綜合損益表')
        df_comprehensive_income = process_comprehensive_income(fetch_year, fetch_season)
        if isinstance(df_comprehensive_income, pd.DataFrame):
            file_name = f'{YEAR}年第{fetch_season}季綜合損益表.csv'
            # TODO: insert into database
        print("===== DONE =====")

        print('現金流量表')
        df_cash_flow = process_cash_flow(fetch_year, fetch_season)
        if isinstance(df_cash_flow, pd.DataFrame):
            file_name = f'{YEAR}年第{fetch_season}季現金流量表.csv'
            # TODO: insert into database
        print("===== DONE =====")

        print('資產負債表')
        df_balance_sheet = process_balance_sheet(fetch_year, fetch_season)
        if isinstance(df_balance_sheet, pd.DataFrame):
            file_name = f'{YEAR}年第{fetch_season}季資產負債表.csv'
            # TODO: insert into database
        print("===== DONE =====")

    # Remove files from temp
    temp_path = Path('./data/temp')
    files = os.listdir(temp_path)
    for f in files:
        if '.csv' in f:
            rm_file_path = temp_path / f
            os.remove(rm_file_path)
        else:
            continue
