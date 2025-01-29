# built-in packages
from io import StringIO
from pathlib import Path
# installed packages
import pandas as pd
import requests
import twstock

twstock.__update_codes()
TEMP_PATH = Path('./data/temp')  # GitHub path


def fetch_monthly_revenue(year: int, month: int):
    print(f"獲取{year}年{month}月營收")
    year_tw = year - 1911
    data = []
    for market in ['sii', 'otc']:  # 上市＋上櫃
        url = f'https://mops.twse.com.tw/nas/t21/{market}/t21sc03_{year_tw}_{month}_0.html'
        response = requests.get(url, timeout=10)
        response.encoding = 'big5'
        html_content = response.text
        if not html_content:
            continue
        dfs = pd.read_html(StringIO(html_content))
        dfs = pd.concat([d for d in dfs if 'levels' in dir(d.columns)])
        dfs.columns = dfs.columns.get_level_values(1)
        data.append(dfs)
    if len(data) == 0:
        print(f"No data {year}-{month}")
        return None
    data = pd.concat(data)
    data.to_csv(TEMP_PATH / f'{year}{str(month).zfill(2)}月營收.csv', index=False)
    return None

def fetch_seasonal_report(year: int, season: int, market_type: str, report_type: str):
    print(year, season, market_type, report_type)
    url = "https://mops.twse.com.tw/mops/web/ajax_t163sb04"  # default 綜合損益表
    if report_type == '資產負債表':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
    if report_type == '現金流量表':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb20"

    typek = 'sii' if market_type == '上市' else 'otc'  # 上市: sii 上櫃: otc
    params = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'isQuery': 'Y',
        'TYPEK': typek,
        'year': year - 1911,
        'season': season,
    }
    response = requests.post(url, params, timeout=10)
    response.encoding = 'utf-8'
    html_content = response.text
    if not html_content:
        return f"No content in {year} Q{season}"
    dfs = pd.read_html(StringIO(html_content))

    # save to GitHub temp folder and upload to Google Drive
    def save_temp_file(dataframe: pd.DataFrame, industry_name: str):
        save_name = f"{year}_Q{season}_{market_type}_{industry_name}_{report_type}.csv"
        dataframe.to_csv(TEMP_PATH / save_name, index=False)

    if market_type == '上市':
        for ind, data in enumerate(dfs):
            if ind == 0:
                pass
            if ind == 1:
                save_temp_file(data, '銀行業')
            if ind == 2:
                save_temp_file(data, '證券業')
            if ind == 3:
                save_temp_file(data, '一般業')
            if ind == 4:
                save_temp_file(data, '金控業')
            if ind == 5:
                save_temp_file(data, '保險業')
            if ind == 6:
                save_temp_file(data, '異業')
    if market_type == '上櫃':
        for ind, data in enumerate(dfs):
            if ind == 0:
                pass
            if ind == 1:
                save_temp_file(data, '金融保險業')
            if ind == 2:
                save_temp_file(data, '一般業')
