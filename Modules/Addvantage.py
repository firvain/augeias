import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

import pytz
from sqlalchemy import create_engine


def addvantage(data_path, file, save_csv=False, csv_name="", plot=False, save_to_db=True, db_mode='replace',
               sep=";"):
    data_folder = Path(data_path)
    file_ = data_folder / file
    df = pd.read_csv(file_, parse_dates=['Date'], encoding="cp1253", sep=sep)

    final_table_columns = ["Date", "Time", "AIR TEMPERATURE (°C)", "WIND SPEED 100 Hz (m/s)", "Precipitation (mm)",
                           "Pyranometer (W/m²)"]
    df["AIR TEMPERATURE (°C)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
    df["WIND SPEED 100 Hz (m/s)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
    df["Precipitation (mm)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
    df["Pyranometer (W/m²)"].replace(to_replace=r'\*', value=0.0, regex=True, inplace=True)
    # print(df.head())
    df = df[df.columns.intersection(final_table_columns)]
    df['Time'] = pd.to_datetime(df['Time']).dt.time
    # df.to_csv('test.csv')

    # df['timestamp'] = df.apply(lambda r: pd.to_datetime.combine(r['Date'], r['Time']), 1)
    df['timestamp'] = pd.to_datetime(df['Date'].astype(str) + df['Time'].astype(str), format='%Y-%m-%d%H:%M:%S')
    # print(df.dtypes)
    my_timezone = pytz.timezone('Europe/Athens')
    df['timestamp'] = df['timestamp'].dt.tz_localize(my_timezone, ambiguous='infer')

    df.set_index('timestamp', inplace=True)

    out_df = df.drop(labels=['Date', 'Time'], axis=1)
    out_df = out_df.astype(np.float64)

    if save_to_db:
        db_url = 'postgresql://nmfzxjvosmhqxs:614adee59cc7aa63f4d128e1ed2c493be7faae3233099962fb189da037340ae9@ec2-34-242-8-97.eu-west-1.compute.amazonaws.com:5432/dfdfjui84brdcr'
        engine = create_engine(db_url)
        out_df.to_sql('addvantage', engine, if_exists=db_mode)
    if save_csv:
        file_ = data_folder / csv_name
        out_df.to_csv(file_)
    if plot:
        selected_rows = out_df[~out_df.isnull().any(axis=1)]
        fig, a = plt.subplots(2, 2, figsize=(12, 6), tight_layout=True)
        selected_rows.plot(ax=a, subplots=True, rot=90)
        plt.savefig('addvantage.png')
        plt.show()

    # print(out_df.interpolate().ffill().bfill())
