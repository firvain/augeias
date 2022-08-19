import os
import uuid

import pandas as pd
import pytz
import requests
import sqlalchemy
import xmltodict
from dotenv import load_dotenv
from pandas import DataFrame, to_datetime
from sqlalchemy import create_engine

from Utils.Pandas_utils import resample_dataset

load_dotenv('.env')
POSTGRESQL_URL = os.environ.get("POSTGRESQL_URL")


def save_df_to_database(df: pd.DataFrame, table_name: str):
    if table_name:
        print(f"saving {table_name} to db")
        engine = create_engine(POSTGRESQL_URL)
        try:
            upsert_df(df=df, table_name=table_name, engine=engine)
        except ValueError as e:
            print(e)
    else:
        print("table name is empty!!!")
        pass


def upsert_df(df: pd.DataFrame, table_name: str, engine: sqlalchemy.engine.Engine):
    """Implements the equivalent of pd.DataFrame.to_sql(..., if_exists='update')
    (which does not exist). Creates or updates the db records based on the
    dataframe records.
    Conflicts to determine update are based on the dataframes index.
    This will set unique keys constraint on the table equal to the index names
    1. Create a temp table from the dataframe
    2. Insert/update from temp table into table_name
    Returns: True if successful
    """

    # If the table does not exist, we should just use to_sql to create it
    if not engine.execute(
            f"""SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE  table_schema = 'public'
            AND    table_name   = '{table_name}');
            """
    ).first()[0]:
        df.to_sql(table_name, engine)
        return True

    # If it already exists...
    temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
    df.to_sql(temp_table_name, engine, index=True)

    index = list(df.index.names)
    index_sql_txt = ", ".join([f'"{i}"' for i in index])
    columns = list(df.columns)
    headers = index + columns
    headers_sql_txt = ", ".join(
        [f'"{i}"' for i in headers]
    )  # index1, index2, ..., column 1, col2, ...

    # col1 = exluded.col1, col2=excluded.col2
    update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])

    # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
    query_pk = f"""
    ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert_{table_name};
    ALTER TABLE "{table_name}" ADD CONSTRAINT unique_constraint_for_upsert_{table_name} UNIQUE ({index_sql_txt});
    """

    engine.execute(query_pk)

    # Compose and execute upsert query
    query_upsert = f"""
    INSERT INTO "{table_name}" ({headers_sql_txt}) 
    SELECT {headers_sql_txt} FROM "{temp_table_name}"
    ON CONFLICT ({index_sql_txt}) DO UPDATE 
    SET {update_column_stmt};
    """
    engine.execute(query_upsert)
    engine.execute(f"DROP TABLE {temp_table_name}")
    engine.dispose()
    return True
