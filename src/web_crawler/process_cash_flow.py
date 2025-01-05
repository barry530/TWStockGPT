import os
from pathlib import Path
import numpy as np
import pandas as pd
FILE_PATH = Path('./data/temp')
COLS = ['證券代號', '證券名稱', '營業現金流', '投資現金流', '籌資現金流', '淨現金流']


def process_cash_flow(year, season):
    files = [f for f in os.listdir(FILE_PATH) if '現金流量表' in f]
    if len(files) == 0:
        return f"No data {FILE_PATH}/現金流量表"
    dfs = []
    for file in files:
        df = pd.read_csv(FILE_PATH / file)
        dfs.append(df)
    data = pd.concat(dfs)
    rename_dict = {
        '公司 代號': '證券代號',
        '營業活動之淨現金流入（流出）': '營業現金流',
        '投資活動之淨現金流入（流出）': '投資現金流',
        '籌資活動之淨現金流入（流出）': '籌資現金流',
        '匯率變動對現金及約當現金之影響': '匯率變動之影響',
        '本期現金及約當現金增加（減少）數': '淨現金流',
    }
    data = data.rename(columns=rename_dict).copy()
    for col in data.columns[2:]:
        data[col] = data[col].replace('--', np.nan).astype('float64')
    data['證券代號'] = data['證券代號'].astype('Int64').astype('str')
    data = data[COLS]
    data['自由現金流'] = data['營業現金流'] + data['投資現金流']  # 企業可自由運用之現金
    data.insert(2, '年度', str(year))
    data.insert(3, '季度', str(season))
    month = ((data['季度'].astype(int) - 1) * 3 + 1).astype(str)
    data.insert(0, 'stat_date', pd.to_datetime(data['年度'].astype(str) + month, format='%Y%m'))
    return data
