import json
import requests
import pandas as pd

import twstock
twstock.__update_codes()

def get_stock_list(date_str: str):
    print("========== 取得股票清單 ==========")
    codes = twstock.codes.keys()
    infos = [twstock.codes[c] for c in codes]
    types = [t.type for t in infos]
    names = [t.name for t in infos]
    markets = [t.market for t in infos]
    groups = [t.group for t in infos]
    df = pd.DataFrame({
        '證券代號': codes,
        '證券名稱': names,
        '類型': types,
        '上市櫃': markets,
        '產業': groups
    })
    df = df[
        (df['上市櫃'].isin(['上市']))  # '上櫃', '上市臺灣創新板'
        & (df['類型'].isin(['股票', 'ETF']))  # '創新板'
        ].copy()
    df.insert(0, 'stat_date', pd.to_datetime(date_str))
    return df

def get_closing_prices(date_str):
    print("========== 成交資訊 ==========")
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=ALLBUT0999"
    res = requests.get(url, timeout=10)
    json_data = json.loads(res.text)
    df = pd.DataFrame()
    if json_data != '很抱歉，沒有符合條件的資料!':
        df = pd.DataFrame(
            json_data['tables'][8]['data'], columns=json_data['tables'][8]['fields']
        )  # 8 每日收盤行情(全部(不含權證、牛熊證))
        df['漲跌價差'] = df['漲跌價差'].astype(float)
        columns = ['證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價',
                   '漲跌價差', '本益比']
        df['漲跌(+/-)'] = \
            df['漲跌(+/-)'].map(lambda x: -1 if x == '<p style= color:green>-</p>' else 1)
        df['漲跌價差'] = \
            (df['漲跌價差'].astype(float) * df['漲跌(+/-)']).astype(str)
        for c in columns[2:]:
            df[c] = pd.to_numeric(df[c].str.replace(',', ''), errors='coerce')
        df = df[columns]
        df.insert(0, 'stat_date', pd.to_datetime(date_str))
    return df

def get_over_buy_and_sell_info(date_str: str):
    print("========== 三大法人買賣超 ==========")
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALLBUT0999&response=json"
    res = requests.get(url, timeout=10)
    json_data = json.loads(res.text)
    df = pd.DataFrame()
    if json_data != '很抱歉，沒有符合條件的資料!':
        columns = json_data['fields']
        df = pd.DataFrame(json_data['data'], columns=columns)
        df.insert(0, 'stat_date', pd.to_datetime(date_str))
        df['證券名稱'] = df['證券名稱'].str.strip()
    return df

def get_daily_exchange_info(today_str):
    df_stocks = get_stock_list(today_str)
    df_closing_prices = get_closing_prices(today_str)
    df_over_buy_sell = get_over_buy_and_sell_info(today_str)
    if (len(df_closing_prices) != 0) and (len(df_over_buy_sell) != 0):
        temp = df_stocks.merge(df_closing_prices, on=['stat_date', '證券代號', '證券名稱'], how='left')
        df_exchange_info = temp.merge(df_over_buy_sell, on=['stat_date', '證券代號', '證券名稱'], how='left')
        df_exchange_info.to_csv(f"./data/temp/{today_str}成交資訊.csv", index=False)
        return df_exchange_info
    else:
        return pd.DataFrame()