import os
from io import StringIO
from pathlib import Path
import pandas as pd
import requests

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES
)
SERVICE = build('drive', 'v3', credentials=CREDENTIALS)

def upload_to_google_drive(file_path, destination):
    """
    upload file to Google Drive
    :param file_path:
    :param destination:
    :return:
    """
    media = MediaFileUpload(file_path)  # create the file object
    file = {'name': file_path, 'parents': [destination]}
    file_id = SERVICE.files().create(body=file, media_body=media).execute()
    print(file_id)

cwd = os.getcwd()
print(cwd)

MONTH_REV_FOLDER = '1KBAR0g6z-akocDe13ZOqvYQin8jjKMXd'
CASH_FLOW_FOLDER = '1IRcQQZCjXjx0mfqTQfEeKVeIvEgUVhMH'
BALANCE_SHEET_FOLDER = '1amiletKSjXBruA1--aYFxXE4J8RAkHwJ'
COMPREHENSIVE_REPORT_FOLDER = '1V8_AJQLiI11zeuX7L4Y41klm6y0Vwvpv'
CSV_SAVE_PATH = Path('./data')  # Github path


def crawl_month_revenue(year: int, month: int):
    """

    :param year: current year
    :param month: current month
    :return: revenue report of previous month with listed companies and open-to-counter companies
    """
    # Crawling monthly revenue
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
        dfs = pd.read_html(StringIO(html_content))
        dfs = pd.concat([d for d in dfs if 'levels' in dir(d.columns)])
        dfs.columns = dfs.columns.get_level_values(1)
        data.append(dfs)
    data = pd.concat(data)
    # save to GitHub -> upload to Google Drive
    # will delete after processing and appending
    save_path = CSV_SAVE_PATH / 'temp' / f'{year}_{str(month).zfill(2)}_monthly_rev.csv'
    data.to_csv(save_path, index=False)
    upload_to_google_drive(save_path, MONTH_REV_FOLDER)

def crawl_seasonal_report(year: int, season: int, market_type, report_type):
    """
    crawl seasonal report and upload to google drive and GitHub temp folder
    :param year: current year
    :param season: previous season
    :param market_type: 上市 / 上櫃
    :param report_type: 綜合損益表 / 資產負債表 / 現金流量表
    :return: previous season with selected market type and selected financial report type
    """
    url = "https://mops.twse.com.tw/mops/web/ajax_t163sb04"  # default 綜合損益表
    google_drive_folder = COMPREHENSIVE_REPORT_FOLDER
    if report_type == '資產負債表':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
        google_drive_folder = BALANCE_SHEET_FOLDER
    if report_type == '現金流量表':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb20"
        google_drive_folder = CASH_FLOW_FOLDER

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
    def save_file_and_upload_to_google_drive(dataframe: pd.DataFrame, industry_name: str):
        save_path = CSV_SAVE_PATH / 'temp' / f"{year}_Q{season}_{market_type}_{industry_name}_{report_type}.csv"
        dataframe.to_csv(save_path, index=False)
        upload_to_google_drive(save_path, google_drive_folder)

    if market_type == '上市':
        for ind, data in enumerate(dfs):
            if ind == 0:
                pass
            if ind == 1:
                save_file_and_upload_to_google_drive(data, '銀行業')
            if ind == 2:
                save_file_and_upload_to_google_drive(data, '證券業')
            if ind == 3:
                save_file_and_upload_to_google_drive(data, '各種產業')
            if ind == 4:
                save_file_and_upload_to_google_drive(data, '金控業')
            if ind == 5:
                save_file_and_upload_to_google_drive(data, '保險業')
            if ind == 6:
                save_file_and_upload_to_google_drive(data, '其他產業')
    if market_type == '上櫃':
        for ind, data in enumerate(dfs):
            if ind == 0:
                pass
            if ind == 1:
                save_file_and_upload_to_google_drive(data, '金融保險業')
            if ind == 2:
                save_file_and_upload_to_google_drive(data, '各種產業')
