import os
from pathlib import Path
import pandas as pd
TEMP_PATH = Path('./data/temp')

def process_monthly_revenue(year, month):
    rename_dict = {
        '公司 代號': '證券代號',
        '公司名稱': '證券名稱',
        '當月營收': '營收',
    }
    file_path = TEMP_PATH / f'{year}年{str(month).zfill(2)}月營收.csv'
    if not os.path.exists(file_path):
        return f"No data {file_path}"
    data = pd.read_csv(file_path)
    cols = ['公司 代號', '公司名稱', '當月營收', '備註']
    data = data[cols].rename(columns=rename_dict)
    data = data.query("~股票代號.str.contains('合計')")
    data.loc[:]['營收'] = pd.to_numeric(data['營收'], 'coerce')
    data = data[~data['營收'].isnull()]
    data.insert(2, '年度', year)
    data.insert(3, '月份', month)
    data.insert(
        0,
        'stat_date',
        pd.to_datetime(data['年度'].astype(str) + data['月份'].astype(str), format='%Y%m')
    )
    data.loc[:]['備註'] = data['備註'].replace('-', pd.NA)
    print(data.shape)
    data.to_csv(file_path, index=False)
    return data
