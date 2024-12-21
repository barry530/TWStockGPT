import os
from pathlib import Path
import numpy as np
import pandas as pd
FILE_PATH = Path('./data/temp')
COLS = ['股票代號', '公司名稱', '流動資產', '非流動資產', '資產總計', '流動負債', '非流動負債', '負債總計',
        '股本', '資本公積', '保留盈餘', '權益總計', '每股參考淨值']


def process_df_generic(input_df, rename_dict, additional_calculation=None):
    """

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
    return data


def process_otc_financial(input_df):
    print('上櫃 金融保險業')
    rename_dict = {
        '公司 代號': '股票代號',
        '保留盈餘（或累積虧損）': '保留盈餘',
    }
    return process_df_generic(input_df, rename_dict)


def process_otc_majority(input_df):
    print('上櫃 各種產業')
    rename_dict = {
        '公司 代號': '股票代號',
    }
    return process_df_generic(input_df, rename_dict)


def process_sii_bank(input_df):
    print('上市 銀行業')
    rename_dict = {
        '公司 代號': '股票代號',
        '資產總額': '資產總計',
        '負債總額': '負債總計',
        '權益總額': '權益總計',
    }
    def calculations(data):
        data['流動資產'] = np.nan
        data['非流動資產'] = np.nan
        data['流動負債'] = np.nan
        data['非流動負債'] = np.nan
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_securities(input_df):
    print('上市 證券業')
    rename_dict = {
        '公司 代號': '股票代號',
        '保留盈餘（或累積虧損）': '保留盈餘',
    }
    return process_df_generic(input_df, rename_dict)


def process_sii_majority(input_df):
    print('上市 各種產業')
    rename_dict = {
        '公司 代號': '股票代號',
    }
    return process_df_generic(input_df, rename_dict)


def process_sii_fin(input_df):
    print('上市 金控業')
    rename_dict = {
        '公司 代號': '股票代號',
        '資產總額': '資產總計',
        '負債總額': '負債總計',
        '權益總額': '權益總計'
    }
    def calculations(data):
        data['流動資產'] = np.nan
        data['非流動資產'] = np.nan
        data['流動負債'] = np.nan
        data['非流動負債'] = np.nan
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_insurance(input_df):
    print('上市 保險業')
    rename_dict = {
        '公司 代號': '股票代號',
    }
    def calculations(data):
        data['流動資產'] = np.nan
        data['非流動資產'] = np.nan
        data['流動負債'] = np.nan
        data['非流動負債'] = np.nan
    return process_df_generic(input_df, rename_dict, calculations)


def process_sii_others(input_df):
    print('上市 其他產業')
    rename_dict = {
        '公司 代號': '股票代號',
        '流動資產': '流動資產',
        '非流動資產': '非流動資產',
        '資產總計': '資產總計',
        '流動負債': '流動負債',
        '非流動負債': '非流動負債',
        '負債總計': '負債總計',
        '股本': '股本',
        '資本公積': '資本公積',
        '保留盈餘': '保留盈餘',
        '權益總額': '權益總計',
        '每股參考淨值': '每股參考淨值'
    }
    return process_df_generic(input_df, rename_dict)


def process_balance_sheet(year, season):
    """
    1. determine which processing function to apply through file name
    2. Directly return the function in the dict
    3. Once we determine a function, send the df as the param and return processed df
    4. if not, raise error
    """
    files = [f for f in os.listdir(FILE_PATH) if '資產負債表' in f]
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
