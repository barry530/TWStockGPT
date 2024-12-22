import os
from pathlib import Path
from financial_report_crawl import crawl_month_revenue, crawl_seasonal_report
from process_monthly_revenue import process_monthly_revenue
from process_comprehensive_imcome import process_comprehensive_income
from process_cash_flow import process_cash_flow
from process_balance_sheet import process_balance_sheet
from datetime import datetime
import pandas as pd

# TODO: 重新上傳幾份資料 調整stat_date (記到10月份)

CSV_SAVE_PATH = Path('./data')  # Github path
MONTH_REV_CSV_PATH = CSV_SAVE_PATH / 'monthly_rev.csv'
COMPREHENSIVE_INCOME_CSV_PATH = CSV_SAVE_PATH / 'comprehensive_income.csv'
CASH_FLOW_CSV_PATH = CSV_SAVE_PATH / 'cash_flow.csv'
BALANCE_SHEET_CSV_PATH = CSV_SAVE_PATH / 'balance_sheet.csv'


if __name__ == '__main__':
    YEAR = datetime.now().year
    MONTH = datetime.now().month
    DAY = datetime.now().day
    SEASON = MONTH // 4 + 1

    # Monthly Revenue Report (Get previous month's report)
    print('Append 月營收')
    print(pd.read_csv(MONTH_REV_CSV_PATH).shape)
    if MONTH == 1:
        crawl_month_revenue(YEAR - 1, 12)
        df_monthly_rev = process_monthly_revenue(YEAR - 1, 12)
    else:
        crawl_month_revenue(YEAR, MONTH-1)
        df_monthly_rev = process_monthly_revenue(YEAR, MONTH-1)
    # Append to the existing file
    df_monthly_rev.to_csv(MONTH_REV_CSV_PATH, mode='a', index=False, header=False)
    print(pd.read_csv(MONTH_REV_CSV_PATH).shape)

    for market_type in ['上市', '上櫃']:
        for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
            if MONTH in [1, 2, 3]:
                print(f"{market_type} {report_type}")
                crawl_seasonal_report(YEAR-1, 4, market_type, report_type)
            else:
                crawl_seasonal_report(YEAR, SEASON-1, market_type, report_type)

    # Comprehensive Income
    print('Append 綜合損益表')
    print(pd.read_csv(COMPREHENSIVE_INCOME_CSV_PATH).shape)
    df_comprehensive_income = process_comprehensive_income(YEAR, SEASON-1)
    df_comprehensive_income.to_csv(
        COMPREHENSIVE_INCOME_CSV_PATH, mode='a', index=False, header=False
    )
    print(pd.read_csv(COMPREHENSIVE_INCOME_CSV_PATH).shape)

    # Cash Flow
    print('Append 現金流量表')
    print(pd.read_csv(CASH_FLOW_CSV_PATH).shape)
    df_cash_flow = process_cash_flow(YEAR, SEASON-1)
    df_cash_flow.to_csv(
        CASH_FLOW_CSV_PATH, mode='a', index=False, header=False
    )
    print(pd.read_csv(CASH_FLOW_CSV_PATH).shape)

    # Balance Sheet
    print('Append 資產負債表')
    print(pd.read_csv(BALANCE_SHEET_CSV_PATH).shape)
    df_balance_sheet = process_balance_sheet(YEAR, SEASON-1)
    df_balance_sheet.to_csv(
        BALANCE_SHEET_CSV_PATH, mode='a', index=False, header=False
    )
    print(pd.read_csv(BALANCE_SHEET_CSV_PATH).shape)

    # Remove files from temp
    temp_path = Path('./data/temp')
    files = os.listdir(temp_path)
    for f in files:
        rm_file_path = temp_path / f
        os.remove(rm_file_path)
