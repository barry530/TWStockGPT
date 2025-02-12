import os
import pandas as pd
from ast import literal_eval
from sqlalchemy import create_engine
from sqlalchemy.sql import text

DB_CONNECTION = literal_eval(os.environ['DB_CONNECTION'])
HOST = DB_CONNECTION['host']
PORT = DB_CONNECTION['port']
USERNAME = DB_CONNECTION['username']
PASSWORD = DB_CONNECTION['password']
DATABASE = DB_CONNECTION['database']
ENGINE = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')

# TODO: trigger actions, backfilling data
def upload_data_to_mysql(dataframe: pd.DataFrame, table_name: str):
    print(f">>>>>>>>>> Upload {dataframe.shape[0]} rows to the table {table_name} <<<<<<<<<<")
    stat_date = dataframe['stat_date'].iloc[0]
    if ('stat_date' in dataframe.columns) and ('證券代號' in dataframe.columns):
        with ENGINE.begin() as conn:
            # use bindparam
            conn.execute(
                text(f"DELETE FROM {table_name} WHERE stat_date = :stat_date"),
                {"stat_date": stat_date}
            )
    dataframe.to_sql(
        table_name,
        con=ENGINE,
        if_exists='append',
        index=False
    )
    print(f"Upload {table_name} successfully!")
