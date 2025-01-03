import os
from pathlib import Path
import pandas as pd
FILE_PATH = Path('./data/temp')

def process_monthly_revenue(year, month):
    """

    :param year:
    :param month:
    :return:
    """
    rename_dict = {
        '公司 代號': '股票代號',
        '公司名稱': '公司名稱',
        '當月營收': '營收',
    }
    file_path = FILE_PATH / f'{year}_{str(month).zfill(2)}_monthly_rev.csv'
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
    return data
