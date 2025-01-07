import json
from datetime import date
import requests
import pandas as pd

import twstock
twstock.__update_codes()
# TODO: 傳至google drive的檔名調整 但是不要更新那幾張csv
# TODO: 日成交資訊更新一張表在Github定時更新
# TODO: 日成交資訊backfill


if __name__ == '__main__':
    today_str = date.today().strftime('%Y%m%d')
    FOLDER = "182cQ9tuK3-CkmLNn66AmzcgwRNTFXW_v"

    print("step1 更新股票")
    codes = twstock.codes.keys()
    infos = [twstock.codes[c] for c in codes]
    types = [t.type for t in infos]
    names = [t.name for t in infos]
    markets = [t.market for t in infos]
    groups = [t.group for t in infos]
    df_stocks = pd.DataFrame({
        '證券代號': codes,
        '證券名稱': names,
        '類型': types,
        '上市櫃': markets,
        '產業': groups
    })
    df_stocks = df_stocks[
        (df_stocks['上市櫃'].isin(['上市']))  # '上櫃', '上市臺灣創新板'
        & (df_stocks['類型'].isin(['股票', 'ETF']))  # '創新板'
        ].copy()
    df_stocks.insert(0, 'stat_date', pd.to_datetime(today_str, format='%Y%m%d'))

    print("step2 成交資訊")
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={today_str}&type=ALLBUT0999"
    res = requests.get(url)
    json_data = json.loads(res.text)
    print(json_data['tables'][8]['title'])
    df_exchange_report = pd.DataFrame(
        json_data['tables'][8]['data'], columns=json_data['tables'][8]['fields']
    )
    # 8 每日收盤行情(全部(不含權證、牛熊證))
    df_exchange_report['漲跌價差'] = df_exchange_report['漲跌價差'].astype(float)
    columns = ['證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '本益比']
    df_exchange_report['漲跌(+/-)'] = \
        df_exchange_report['漲跌(+/-)'].map(lambda x: -1 if x == '<p style= color:green>-</p>' else 1)
    df_exchange_report['漲跌價差'] = \
        (df_exchange_report['漲跌價差'].astype(float) * df_exchange_report['漲跌(+/-)']).astype(str)
    for c in columns[2:]:
        # print(df[c].str.replace(',', ''))
        df_exchange_report[c] = pd.to_numeric(df_exchange_report[c].str.replace(',', ''), errors='coerce')
    df_exchange_report = df_exchange_report[columns]
    df_exchange_report.insert(0, 'stat_date', pd.to_datetime(today_str, format='%Y%m%d'))

    print("step3 三大法人買賣超")
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={today_str}&selectType=ALLBUT0999&response=json"
    res = requests.get(url)
    json_data = json.loads(res.text)
    columns = json_data['fields']
    df_over_buy_sell = pd.DataFrame(json_data['data'], columns=columns)
    df_over_buy_sell.insert(0, 'stat_date', pd.to_datetime(today_str, format='%Y%m%d'))
    df_over_buy_sell['證券名稱'] = df_over_buy_sell['證券名稱'].str.strip()

    temp = df_stocks.merge(df_exchange_report, on=['stat_date', '證券代號', '證券名稱'], how='left')
    df = temp.merge(df_over_buy_sell, on=['stat_date', '證券代號', '證券名稱'], how='left')
