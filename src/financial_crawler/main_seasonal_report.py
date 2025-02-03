import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
from src.utils.utils import upload_data_to_mysql
from scrape_financial_report import scrape_seasonal_report
from process_comprehensive_income import process_comprehensive_income
from process_cash_flow import process_cash_flow
from process_balance_sheet import process_balance_sheet

TEMP_PATH = Path('./data/temp')  # GitHub path

if __name__ == '__main__':
    # 第一季：5月15日前
    # 第二季：8月14日前
    # 第三季：11月14日前
    # 第四季：3月15日前，其餘應在4月1日前
    # 金融股、KY股不在此限，在月底前公布即可
    TODAY = date.today()
    YESTERDAY = TODAY - timedelta(days=1)
    YEAR = TODAY.year
    MONTH = TODAY.month
    DAY = TODAY.day
    today_str = TODAY.strftime('%Y%m%d')
    yesterday_str = YESTERDAY.strftime('%Y-%m-%d')

    if MONTH in [6, 9, 12, 4] and DAY == 1:


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
                scrape_seasonal_report(fetch_year, fetch_season, market_type, report_type)

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
