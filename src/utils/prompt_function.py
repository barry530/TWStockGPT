import pandas as pd
from get_data import get_monthly_revenue_numbers, get_seasonal_report_numbers

df_stocks = pd.read_csv("./data/stock_list.csv")
STOCK_NAMES = set(df_stocks['公司名稱'].unique())
STOCK_CODE_NAME_MAPPING = {}
for ind, row in df_stocks.iterrows():
    STOCK_CODE_NAME_MAPPING[row['股票代號']] = row['公司名稱']

DISPLAY_N_MONTH = 6
DISPLAY_N_SEASON = 1

def detect_ticker(sentence: str):
    """
    Detect if there are stock name/code in the sentence
    :param sentence: input text
    :return: A set of stock name(s)
    """
    tickers = []
    # detect stock name
    for keyword in STOCK_NAMES:
        if keyword in sentence:
            tickers.append(keyword)

    # detect stock code and convert to name
    for key, item in STOCK_CODE_NAME_MAPPING.items():
        if key in sentence:
            tickers.append(item)
    return set(tickers)

def monthly_rev_numbers_str(stock_name: str):
    """

    :param stock_name:
    :return:
    """
    df = get_monthly_revenue_numbers(stock_name, DISPLAY_N_MONTH)
    df = df.sort_values('stat_date', ascending=False)
    stock_name = df['公司名稱'].unique()[0]
    stock_code = df['股票代號'].unique()[0]
    start = f'{stock_name}（{stock_code}）過去{DISPLAY_N_MONTH}個月的營收如下：'
    res = []
    for y, m, rev in zip(df['年度'], df['月份'], df['營收']):
        text = f"- {y}年{m}月營收：{format(rev, ',')}"
        res.append(text)
    res = [start] + res
    return '\n'.join(res)

def seasonal_report_numbers_str(stock_name: str, report_type: str):
    """
    綜合損益表：
    1.毛利率：營業毛利／營業收入 × 100%（可用於比較同業之間的「產業地位」和「產品價值」）
    2.營益率：營業利益／營業收入 × 100%（可用於判斷企業經營「本業」的管銷能力）
    3.淨利率：稅後淨利／營業收入 × 100%（可用於間接判斷企業的「業外收入」情形）
    """
    df = get_seasonal_report_numbers(stock_name, report_type, DISPLAY_N_SEASON)
    df = df.sort_values('stat_date', ascending=False)
    stock_name = df['公司名稱'].unique()[0]
    stock_code = df['股票代號'].unique()[0]
    start = f'{stock_name}（{stock_code}）過去{DISPLAY_N_SEASON}季的{report_type}數字如下：'
    res = []
    if report_type == '綜合損益表':
        df['毛利率'] = df['營業毛利'] / df['營業收入']
        df['營益率'] = df['營業利益'] / df['營業收入']
        df['淨利率'] = df['稅後淨利'] / df['營業收入']
        display_numbers = ['營業毛利', '營業利益', '稅後淨利', '毛利率', '營益率', '淨利率']

    elif report_type == '資產負債表':
        display_numbers = ['資產總計', '負債總計', '權益總計', '每股參考淨值']

    else:  # 現金流量表
        display_numbers = ['營業現金流', '投資現金流', '籌資現金流', '淨現金流', '自由現金流']

    for y, s in zip(df['年度'], df['季度']):
        for c in display_numbers:
            number = df.loc[(df['年度'] == y) & (df['季度'] == s), c].values[0]
            text = f"- {y}年第{s}季{c}：{format(number, ',')}"
            res.append(text)

    res = [start] + res
    return '\n'.join(res)
