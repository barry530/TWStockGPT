import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from datetime import date
from pathlib import Path
import pandas as pd
from utils.db_funcs import upload_data_to_mysql
from financial_crawler.scrape_financial_report import scrape_monthly_revenue

# pd.set_option('future.no_silent_downcasting', True)
TEMP_PATH = Path('./data/temp')

def process_monthly_revenue(year, month):
    rename_dict = {
        '公司 代號': '證券代號',
        '公司名稱': '證券名稱',
        '當月營收': '營收',
    }
    file_path = TEMP_PATH / f'{year}{str(month).zfill(2)}月營收.csv'
    if not os.path.exists(file_path):
        return f"{year}-{month} 月營收無資料"
    data = pd.read_csv(file_path)
    cols = ['公司 代號', '公司名稱', '當月營收', '備註']
    data = data[cols].rename(columns=rename_dict)
    data = data.query("~證券代號.str.contains('合計')")
    data.loc[:, '營收'] = pd.to_numeric(data['營收'], 'coerce')
    data = data[~data['營收'].isnull()]
    data.insert(2, '年度', year)
    data.insert(3, '月份', month)
    data.insert(
        0,
        'stat_date',
        pd.to_datetime(data['年度'].astype(str) + data['月份'].astype(str), format='%Y%m')
    )
    data.loc[:, '備註'] = data['備註'].replace('-', pd.NA)
    print(data.shape)
    data.to_csv(file_path, index=False)
    return data


if __name__ == '__main__':
    print("==================== 執行月營收爬蟲 ====================")
    year = date.today().year
    month = date.today().month
    day = date.today().day
    if day == 12:
        # 月報：次月10日前公布
        # At 12th (UTC) of every month (in case 10th is Saturday and being postponed)
        print("========== 月營收 ==========")
        if month == 1:
            fetch_year = year - 1
            fetch_month = 12
        else:
            fetch_year = year
            fetch_month = month - 1
        scrape_monthly_revenue(fetch_year, fetch_month)
        df_monthly_rev = process_monthly_revenue(fetch_year, fetch_month)
        if isinstance(df_monthly_rev, pd.DataFrame):
            upload_data_to_mysql(df_monthly_rev, 'monthly_revenue')
        else:
            print(df_monthly_rev)
        print("========== DONE ==========")
    else:
        sys.exit(0)
