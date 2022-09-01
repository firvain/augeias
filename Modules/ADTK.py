import datetime as dt
from datetime import datetime as dt
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
from sqlalchemy import create_engine
from adtk.data import validate_series
from adtk.visualization import plot
from adtk.detector import SeasonalAD
from adtk.detector import ThresholdAD
from colorama import Fore, init

init(autoreset=True)
engine = create_engine('postgresql://augeias:augeias@83.212.19.17:5432/augeias')


def calc_anomalies_ADKT(out_path: str, table_name: str):
    print(f'{Fore.BLUE}Working on table {table_name}')
    try:
        sql = f"""select * from "{table_name}" order by timestamp"""
        data = pd.read_sql(sql, con=engine, index_col="timestamp")

    except ValueError as e:
        print(f'{Fore.RED}{e}')
        pass
    # df = pd.read_csv('spx.csv', parse_dates=['date'], index_col='date')

    end = data.index[-1].to_pydatetime()
    start = data.index[0].to_pydatetime()
    print(f'{Fore.GREEN}start: {start}, {Fore.MAGENTA}end: {end}')
    r = pd.date_range(start=start, end=end).difference(data.index)
    if len(r) != 0:
        idx = pd.date_range(start, end)
        data = data.reindex(idx)
        data.fillna(method="ffill", inplace=True)
    print(f'data shape {data.shape}')
    data = validate_series(data)
    # plot(data)
    # plt.show()
    columns = data.columns.tolist()
    for col in columns:
        print(f'{Fore.BLUE}Working on col: {col}')
        test = data[col]
        print(f'test shape: {test.shape}')

        try:
            min_val = data[col].min()
            max_val = data[col].max()
            print(f'Minimum {col} price {min_val}')
            print(f'Maximum {col} price {max_val}')

            threshold_val = ThresholdAD(high=max_val * .99, low=min_val * 1.01)
            anomalies = threshold_val.detect(data[col])

            # seasonal_vol = SeasonalAD()
            # anomalies = seasonal_vol.fit_detect(test)
            anomalies_true = anomalies.where(lambda x: x).dropna()
            print(f'anomalies shape {anomalies_true.shape}')
            plot(data[col], anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5,
                 anomaly_color='black');
            # plt.show()
            out_folder = Path(f'{out_path}/{table_name}')
            out_folder.mkdir(parents=True, exist_ok=True)
            plt.savefig(out_folder / f'{table_name}_anomalies_{col}.png')
            plt.close()

            df = data[col].loc[anomalies_true.index]
            df.to_csv(f'{out_folder}/{table_name}_anomalies_{col}.csv')
        except BaseException as e:
            print(f'{Fore.RED}{e}')
            pass
    # plot(data, anomaly=anomalies, anomaly_color="orange", anomaly_tag="marker")
    # plt.show()
