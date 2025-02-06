import os
import pandas as pd
from ast import literal_eval
from sqlalchemy import create_engine

# DB_CONNECTION = literal_eval(os.environ['DB_CONNECTION'])
# HOST = DB_CONNECTION['host']
# PORT = DB_CONNECTION['port']
# USERNAME = DB_CONNECTION['username']
# PASSWORD = DB_CONNECTION['password']
# DATABASE = DB_CONNECTION['database']
# print(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
# ENGINE = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')


def upload_data_to_mysql(dataframe: pd.DataFrame, table_name: str):
    print(dataframe.head(3))
    print(dataframe.shape)
    # dataframe.to_sql(
    #     table_name,
    #     con=ENGINE,
    #     if_exists='append',
    #     index=False
    # )
    print(f"Upload {table_name} successfully!")
