import os
from pathlib import Path
import numpy as np
import pandas as pd
FILE_PATH = Path('./data/temp')

COLS = ['股票代號', '公司名稱', '營業收入', '營業成本', '營業毛利', '營業費用',
        '營業利益', '業外收支', '稅前淨利', '所得稅', '稅後淨利', 'EPS']


def formula_check(data):
    """
    Check if the values are very different.
    :param data: dataframe
    :return: log of validating data
    """
    rev_cost_profit = ((data['營業收入'] - data['營業成本'] - data['營業毛利']).sum() / len(data)).round(2)
    print("平均（營業收入－營業成本－營業毛利）：%d", rev_cost_profit)
    income_before_after_tax = (
            (data['稅前淨利'] - data['所得稅'] - data['稅後淨利']).sum() / len(data)
    ).round(2)
    print("平均（稅前淨利－所得稅－稅後淨利）%d", income_before_after_tax)


def process_df_generic(input_df, rename_dict, additional_calculation=None):
    """
    general processing...
    :param input_df: pd.DataFrame
    :param rename_dict: columns rename dict
    :param additional_calculation: columns calculation
    :return: processed dataframe
    """
    data = input_df.rename(columns=rename_dict).copy()
    for col in data.columns[2:]:
        data[col] = data[col].replace('--', np.nan).astype('float64').copy()
    data['股票代號'] = data['股票代號'].astype('Int64').astype('str')
    if additional_calculation:
        additional_calculation(data)
    data = data[COLS]
    formula_check(data)
    return data


def process_otc_financial(input_df):
    print('上櫃 金融保險業')
    rename_dict = {
        '公司 代號': '股票代號',
        '收益': '營業收入',
        '支出及費用': '營業成本',
        '營業外損益': '業外收支',
        '稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    def calculations(data):
        data['營業毛利'] = data['營業收入'] - data['營業成本']
        data['營業費用'] = data['營業毛利'] - data['營業利益']
        data['營業利益'] = data['稅前淨利'] - data['業外收支']
    return process_df_generic(input_df, rename_dict, calculations)


def process_otc_majority(input_df):
    print('上櫃 各種產業')
    rename_dict = {
        '公司 代號': '股票代號',
        '營業毛利（毛損）淨額': '營業毛利',
        '營業利益（損失）': '營業利益',
        '營業外收入及支出': '業外收支',
        '稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    return process_df_generic(input_df, rename_dict)


def process_sii_bank(input_df):
    print('上市 銀行業')
    rename_dict = {
        '公司 代號': '股票代號',
        '呆帳費用、承諾及保證責任準備提存': '營業成本',
        '繼續營業單位稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期稅後淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    def calculations(data):
        data['營業收入'] = data['利息淨收益'] + data['利息以外淨損益']
        data['營業毛利'] = data['營業收入'] - data['營業成本']
        data['營業利益'] = data['營業毛利'] - data['營業費用']
        data['業外收支'] = data['稅前淨利'] - data['營業利益']
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_securities(input_df):
    print('上市 證券業')
    rename_dict = {
        '公司 代號': '股票代號',
        '收益': '營業收入',
        '支出及費用': '營業成本',
        '營業外損益': '業外收支',
        '稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    def calculations(data):
        data['營業毛利'] = data['營業收入'] - data['營業成本']
        data['營業費用'] = data['營業毛利'] - data['營業利益']
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_majority(input_df):
    print('上市 各種產業')
    rename_dict = {
        '公司 代號': '股票代號',
        '營業毛利（毛損）': '營業毛利',
        '營業利益（損失）': '營業利益',
        '營業外收入及支出': '業外收支',
        '稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    return process_df_generic(input_df, rename_dict)


def process_sii_fin(input_df):
    print('上市 金控業')
    rename_dict = {
        '公司 代號': '股票代號',
        '淨收益': '營業毛利',
        '繼續營業單位稅前損益': '稅前淨利',
        '所得稅（費用）利益': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }
    def calculations(data):
        data['營業收入'] = data['營業毛利'] + data['呆帳費用、承諾及保證責任準備提存'] + data['保險負債準備淨變動']  # 推算
        data['營業成本'] = data['呆帳費用、承諾及保證責任準備提存'] + data['保險負債準備淨變動']  # 推算
        data['營業利益'] = data['營業毛利'] - data['營業費用']
        data['業外收支'] = data['稅前淨利'] - data['營業利益']  # 推算
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_insurance(input_df):
    print('上市 保險業')
    rename_dict = {
        '公司 代號': '股票代號',
        '營業利益（損失）': '營業利益',
        '營業外收入及支出': '業外收支',
        '繼續營業單位稅前純益（純損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期純益（純損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS',
    }

    def calculations(data):
        data['營業毛利'] = data['營業收入'] - data['營業成本']  # =營業費用+營業利益

    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_others(input_df):
    print('上市 其他產業')
    rename_dict = {
        '公司 代號': '股票代號',
        '收入': '營業收入',
        '支出': '營業成本',
        '繼續營業單位稅前淨利（淨損）': '稅前淨利',
        '所得稅費用（利益）': '所得稅',
        '繼續營業單位本期淨利（淨損）': '稅後淨利',
        '基本每股盈餘（元）': 'EPS'
    }

    def calculations(data):
        data['營業毛利'] = data['營業收入'] - data['營業成本']  # =營業費用+營業利益
        data['營業費用'] = np.nan
        data['營業利益'] = np.nan
        data['業外收支'] = np.nan

    return process_df_generic(input_df, rename_dict, calculations)


def process_comprehensive_income(year, season):
    """
    1. determine which processing function to apply through file name
    2. Directly return the function in the dict
    3. Once we determine a function, send the df as the param and return processed df
    4. if not, raise error
    """
    files = [f for f in os.listdir(FILE_PATH) if '綜合損益表' in f]
    if len(files) == 0:
        return f"No data {FILE_PATH}/綜合損益表"
    dfs = []
    for file in files:
        df = pd.read_csv(FILE_PATH / file)
        if ("上市" in file) and ("保險業" in file):
            df = process_sii_insurance(df)
        elif "上市" in file and "證券業" in file:
            df = process_sii_securities(df)
        elif "上市" in file and "金控業" in file:
            df = process_sii_fin(df)
        elif "上市" in file and "銀行業" in file:
            df = process_sii_bank(df)
        elif "上市" in file and "各種產業" in file:
            df = process_sii_majority(df)
        elif "上市" in file and "其他產業" in file:
            df = process_sii_others(df)
        elif "上櫃" in file and "各種產業" in file:
            df = process_otc_majority(df)
        elif "上櫃" in file and "金融保險業" in file:
            df = process_otc_financial(df)
        else:
            raise ValueError("未知的資料處理類型")
        dfs.append(df)

    data = pd.concat(dfs)
    data.insert(2, '年度', str(year))
    data.insert(3, '季度', str(season))
    month = ((data['季度'].astype(int) - 1) * 3 + 1).astype(str)
    data.insert(0, 'stat_date', pd.to_datetime(data['年度'].astype(str) + month, format='%Y%m'))
    return data
