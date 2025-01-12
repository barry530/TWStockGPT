import os
from pathlib import Path
from ast import literal_eval

from datetime import date
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

from fetch_financial_report import fetch_monthly_revenue, fetch_seasonal_report
from process_monthly_revenue import process_monthly_revenue
from process_comprehensive_imcome import process_comprehensive_income
from process_cash_flow import process_cash_flow
from process_balance_sheet import process_balance_sheet
from fetch_daily_exchange import get_daily_exchange_info
from src.utils.utils import upload_to_google_drive

GOOGLE_CREDENTIALS = literal_eval(os.environ['GOOGLE_CREDENTIALS'])
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=SCOPES
)
SERVICE = build('drive', 'v3', credentials=CREDENTIALS)

TEMP_PATH = Path('./data/temp')  # Github path

DAILY_EXCHANGE_INFO_FOLDER = "182cQ9tuK3-CkmLNn66AmzcgwRNTFXW_v"
MONTH_REV_FOLDER = '1KBAR0g6z-akocDe13ZOqvYQin8jjKMXd'
CASH_FLOW_FOLDER = '1IRcQQZCjXjx0mfqTQfEeKVeIvEgUVhMH'
BALANCE_SHEET_FOLDER = '17aJjV-eljetrsirtB6PZpbR8-5JzKUjJ'
COMPREHENSIVE_REPORT_FOLDER = '1V8_AJQLiI11zeuX7L4Y41klm6y0Vwvpv'


if __name__ == '__main__':
    # 每日交易：每個工作天
    # 月報：下個月12
    # 季報：下一季第一天
    TODAY = date.today()
    YEAR = TODAY.year
    MONTH = TODAY.month
    DAY = TODAY.day

    print("========== 每日成交資訊 ==========")
    if TODAY.weekday() < 5:  # Monday(0) to Friday(4)
        today_str = TODAY.strftime('%Y%m%d')
        df_daily_exchange_info = get_daily_exchange_info(today_str)
        if len(df_daily_exchange_info) > 0:
            file_name = f"{today_str}成交資訊.csv"
            upload_to_google_drive(
                service=SERVICE,
                file_path=TEMP_PATH / file_name,
                file_name=file_name,
                destination=DAILY_EXCHANGE_INFO_FOLDER
            )
        else:
            print(f"{today_str}無成交資訊")

    # Monthly Revenue Report (Get previous month's report)
    if DAY == 12:  # 次月的10日之前，抓12
        print('月營收爬蟲')
        if MONTH == 1:  # 拿去年12月
            YEAR -= 1
            MONTH = 12
            fetch_monthly_revenue(YEAR, MONTH)
            df_monthly_rev = process_monthly_revenue(YEAR, MONTH)
        else:
            MONTH -= 1
            fetch_monthly_revenue(YEAR, MONTH)
            df_monthly_rev = process_monthly_revenue(YEAR, MONTH)

        if isinstance(df_monthly_rev, pd.DataFrame):
            file_name = f'{YEAR}年{str(MONTH).zfill(2)}月營收.csv'
            upload_to_google_drive(
                service=SERVICE,
                file_path=TEMP_PATH / file_name,
                file_name=file_name,
                destination=MONTH_REV_FOLDER
            )
        print("========== DONE ==========")

    if MONTH in [6, 9, 12, 4] and DAY == 1:
        # 第一季：5月15日前
        # 第二季：8月14日前
        # 第三季：11月14日前
        # 第四季：3月15日前，其餘應在4月1日前
        # 但金融股、KY股不在此限，在月底前公布即可

        print('財務報表')
        for market_type in ['上市', '上櫃']:
            for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
                if MONTH == 4:  # 拿去年第四季
                    print(f"{market_type} {report_type}")
                    SEASON = 4
                    YEAR -= 1
                    fetch_seasonal_report(YEAR, SEASON, market_type, report_type)
                else:
                    SEASON = MONTH // 3 - 1  # 拿上季報表
                    fetch_seasonal_report(YEAR, SEASON, market_type, report_type)

        # Comprehensive Income
        print('綜合損益表')
        df_comprehensive_income = process_comprehensive_income(YEAR, SEASON)
        if isinstance(df_comprehensive_income, pd.DataFrame):
            file_name = f'{YEAR}年第{SEASON}季綜合損益表.csv'
            upload_to_google_drive(
                service=SERVICE,
                file_path=TEMP_PATH / file_name,
                file_name=file_name,
                destination=COMPREHENSIVE_REPORT_FOLDER
            )
        print("========== DONE ==========")

        # Cash Flow
        print('現金流量表')
        df_cash_flow = process_cash_flow(YEAR, SEASON)
        if isinstance(df_cash_flow, pd.DataFrame):
            file_name = f'{YEAR}年第{SEASON}季現金流量表.csv'
            upload_to_google_drive(
                service=SERVICE,
                file_path=TEMP_PATH / file_name,
                file_name=file_name,
                destination=CASH_FLOW_FOLDER
            )
        print("========== DONE ==========")

        # Balance Sheet
        print('資產負債表')
        df_balance_sheet = process_balance_sheet(YEAR, SEASON)
        if isinstance(df_balance_sheet, pd.DataFrame):
            file_name = f'{YEAR}年第{SEASON}季資產負債表.csv'
            upload_to_google_drive(
                service=SERVICE,
                file_path=TEMP_PATH / file_name,
                file_name=file_name,
                destination=BALANCE_SHEET_FOLDER
            )
        print("========== DONE ==========")

    # Remove files from temp
    temp_path = Path('./data/temp')
    files = os.listdir(temp_path)
    for f in files:
        if '.csv' in f:
            rm_file_path = temp_path / f
            os.remove(rm_file_path)
        else:
            continue
