import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from pathlib import Path
from datetime import date
import pandas as pd
from utils.db_funcs import upload_data_to_mysql
from financial_crawler.scrape_financial_report import scrape_seasonal_report
from financial_crawler.process_comprehensive_income import process_comprehensive_income
from financial_crawler.process_cash_flow import process_cash_flow
from financial_crawler.process_balance_sheet import process_balance_sheet

if __name__ == '__main__':
    # 第一季：5月15日前
    # 第二季：8月14日前
    # 第三季：11月14日前
    # 第四季：3月15日前，其餘應在4月1日前
    # 金融股、KY股不在此限，在月底前公布即可
    TODAY = date.today()
    YEAR = TODAY.year
    MONTH = TODAY.month

    print('========== 財務報表爬蟲 ==========')
    for market_type in ['上市', '上櫃']:
        for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
            if MONTH <= 4:  # 拿去年第四季
                fetch_season = 4
                fetch_year = YEAR - 1
            else:
                fetch_season = MONTH // 3 - 1  # 拿上季報表
                fetch_year = YEAR
            scrape_seasonal_report(fetch_year, fetch_season, market_type, report_type)
            print(f"{market_type} {report_type} 報表爬蟲成功")

    print('綜合損益表')
    df_comprehensive_income = process_comprehensive_income(fetch_year, fetch_season)
    if isinstance(df_comprehensive_income, pd.DataFrame):
        upload_data_to_mysql(df_comprehensive_income, 'comprehensive_income')
    print("===== DONE =====")

    print('現金流量表')
    df_cash_flow = process_cash_flow(fetch_year, fetch_season)
    if isinstance(df_cash_flow, pd.DataFrame):
        upload_data_to_mysql(df_cash_flow, 'cash_flow')
    print("===== DONE =====")

    print('資產負債表')
    df_balance_sheet = process_balance_sheet(fetch_year, fetch_season)
    if isinstance(df_balance_sheet, pd.DataFrame):
        upload_data_to_mysql(df_balance_sheet, 'balance_sheet')
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
