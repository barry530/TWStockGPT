import pandas as pd
from pathlib import Path

data_path = Path('./data')
DF_MONTHLY_REV = pd.read_csv(data_path / 'monthly_rev.csv')
DF_MONTHLY_REV.stat_date = pd.to_datetime(DF_MONTHLY_REV.stat_date)

DF_CASH_FLOW = pd.read_csv(data_path / 'cash_flow.csv')
DF_CASH_FLOW.stat_date = pd.to_datetime(DF_CASH_FLOW.stat_date)

DF_BALANCE_SHEET = pd.read_csv(data_path / 'balance_sheet.csv')
DF_BALANCE_SHEET.stat_date = pd.to_datetime(DF_BALANCE_SHEET.stat_date)

DF_COMPREHENSIVE_REPORT = pd.read_csv(data_path / 'comprehensive_income.csv')
DF_COMPREHENSIVE_REPORT.stat_date = pd.to_datetime(DF_COMPREHENSIVE_REPORT.stat_date)


def get_monthly_revenue_numbers(stock_name: str, past_n_months: int):
    """
    Get numbers from
    :param stock_name:
    :param past_n_months:
    :return:
    """
    cond = DF_MONTHLY_REV['公司名稱'] == stock_name
    result = DF_MONTHLY_REV[cond].sort_values('stat_date').tail(past_n_months)
    return result


def get_seasonal_report_numbers(stock_name: str, report_type: str, past_n_seasons: int):
    """

    :param stock_name:
    :param report_type:
    :param past_n_seasons:
    :return:
    """
    if report_type not in ['現金流量表', '資產負債表', '綜合損益表']:
        raise ValueError("report_type should be one of ['現金流量表', '資產負債表', '綜合損益表']")
    if report_type == '現金流量表':
        df_seasonal_report = DF_CASH_FLOW.copy()
    elif report_type == '資產負債表':
        df_seasonal_report = DF_BALANCE_SHEET.copy()
    else:  # report_type == '綜合損益表'
        df_seasonal_report = DF_COMPREHENSIVE_REPORT.copy()
    cond = df_seasonal_report['公司名稱'] == stock_name
    result = df_seasonal_report[cond].sort_values('stat_date').tail(past_n_seasons)
    return result