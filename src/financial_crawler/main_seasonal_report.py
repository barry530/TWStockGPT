import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from datetime import date
import pandas as pd
from utils.db_funcs import upload_data_to_mysql
from financial_crawler.scrape_financial_report import scrape_seasonal_report
from financial_crawler.process_comprehensive_income import process_comprehensive_income
from financial_crawler.process_cash_flow import process_cash_flow
from financial_crawler.process_balance_sheet import process_balance_sheet

if __name__ == '__main__':
    year = date.today().year
    month = date.today().month
    day = date.today().day
    if (month in [4, 6, 9, 12]) and (day == 1):
        # 第一季：5月15日前 -> 1st June
        # 第二季：8月14日前 -> 1st Sept
        # 第三季：11月14日前 -> 1st Dec
        # 第四季：3月15日前 -> 1st Apr
        # 金融股、KY股不在此限，在月底前公布即可
        print('========== 財務報表爬蟲 ==========')
        for market_type in ['上市', '上櫃']:
            for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
                if month <= 4:  # 拿去年第四季
                    fetch_season = 4
                    fetch_year = year - 1
                else:
                    fetch_season = month // 3 - 1  # 拿上季報表
                    fetch_year = year
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

    else:
        sys.exit(0)