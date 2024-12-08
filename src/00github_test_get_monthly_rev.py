import os
from io import StringIO
from pathlib import Path
from datetime import datetime
import pandas as pd
import requests

MONTH_REV_CSV_PATH = Path('./data/monthly_rev.csv')


def crawl_and_process_month_revenue(year: int, month: int):
    """
    :param year: current year
    :param month: current month
    :return: revenue report of previous month with listed companies and open-to-counter companies
    """

    ##### Crawling monthly revenue
    print(year, month)
    year_tw = year - 1911
    data = []
    for market in ['sii', 'otc']:  # 上市＋上櫃
        url = f'https://mops.twse.com.tw/nas/t21/{market}/t21sc03_{year_tw}_{month}_0.html'
        response = requests.get(url, timeout=10)
        response.encoding = 'big5'
        html_content = response.text
        if not html_content:
            continue
        df = pd.read_html(StringIO(html_content))
        df = pd.concat([d for d in df if 'levels' in dir(d.columns)])
        df.columns = df.columns.get_level_values(1)
        data.append(df)
    data = pd.concat(data)

    ##### Process the data
    rename_dict = {
        '公司 代號': '股票代號',
        '公司名稱': '公司名稱',
        '當月營收': '營收',
    }
    cols = ['公司 代號', '公司名稱', '當月營收', '備註']
    data = data[cols].rename(columns=rename_dict)
    data = data.query("~股票代號.str.contains('合計')")
    data.loc[:]['營收'] = pd.to_numeric(data['營收'], 'coerce')
    data = data[~data['營收'].isnull()]
    data.insert(2, '年度', year)
    data.insert(3, '月份', month)
    data.insert(
        0,
        'statdate',
        pd.to_datetime(data['年度'].astype(str) + data['月份'].astype(str), format='%Y%m')
    )
    data.loc[:]['備註'] = data['備註'].replace('-', pd.NA)
    print(data.shape)

    ##### Append to the existing file
    data.to_csv(MONTH_REV_CSV_PATH, mode='a', index=False, header=False)


if __name__ == '__main__':
    YEAR = 2024
    MONTH = 11
    print(pd.read_csv(MONTH_REV_CSV_PATH).shape)
    # Monthly Revenue Report (Get previous month's report)
    if MONTH == 1:
        crawl_and_process_month_revenue(YEAR - 1, 12)
    crawl_and_process_month_revenue(YEAR, MONTH - 1)
    print(pd.read_csv(MONTH_REV_CSV_PATH).shape)
