import json
import os
from datetime import datetime

import numpy as np
import pytz
import requests
from colorama import init
from dotenv import load_dotenv
import pandas as pd
from natsort import natsorted

from Utils.Database import save_df_to_database

init(autoreset=True)
load_dotenv('.env')

api_key = os.environ.get("OPENWEATHER_API_KEY")


def get_openweather_daily(save_to_db: bool = True):
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat=40.2989955&lon=21.7822009&appid=' + api_key + '&exclude=current,minutely,daily,alerts&units=metric'
    print(url)
    try:
        response = requests.get(url)
        data = json.loads(response.text)

        print(len(data['hourly']))
        # out_data = np.empty(shape=(11, len(data['hourly'])))
        my_list = []
        for entry in data['hourly']:
            dt = datetime.fromtimestamp(entry["dt"], pytz.UTC)

            temp = entry["temp"]
            pressure = entry['pressure']
            humidity = entry['humidity']
            dew_point = entry['dew_point']
            uvi = entry['uvi']
            clouds = entry['clouds']
            visibility = entry['visibility']
            wind_speed = entry['wind_speed']
            wind_deg = entry['wind_deg']
            wind_gust = entry['wind_gust']
            my_list.append([dt, temp, pressure, humidity, dew_point, uvi, clouds, visibility, wind_speed, wind_deg,
                            wind_gust])
        df = pd.DataFrame(my_list,
                          columns=['timestamp', 'temp', 'pressure', 'humidity', 'dew_point', 'uvi', 'clouds',
                                   'visibility',
                                   'wind_speed', 'wind_deg',
                                   'wind_gust'])
        df.set_index('timestamp', inplace=True)
        if save_to_db and not df.empty:
            save_df_to_database(df=df[:24], table_name="openweather_direct")
        else:
            print(df[:24])
            raise Exception('no data returned')
    except Exception as e:
        print(e)


def load_openweather_from_csv(save_to_db: bool = False, csv_path: str = ''):
    df = pd.read_csv(csv_path)

    hourly = df.filter(regex='hourly')

    hourly = hourly.reindex(natsorted(hourly.columns), axis=1)

    hourly = hourly[hourly.columns.drop(list(hourly.filter(regex='feels_like')))]
    hourly = hourly[hourly.columns.drop(list(hourly.filter(regex='pop')))]

    hourly = hourly[hourly.columns.drop(list(hourly.filter(regex='weather_0_id')))]
    hourly = hourly[hourly.columns.drop(list(hourly.filter(regex='weather_1_id')))]

    col_names = ['clouds', 'dew_point', 'dt', 'humidity', 'pressure', 'rain_1h', 'snow_1h', 'temp', 'uvi', 'visibility',
                 'wind_deg', 'wind_gust', 'wind_speed']
    df2 = pd.DataFrame(columns=col_names)
    for h in range(48):
        h1 = hourly.filter(regex='_' + str(h) + '_')
        h1.columns = h1.columns.str.lstrip(f'hourly_')
        h1.columns = h1.columns.str.lstrip(f'_{h}_')
        # print(pd.to_datetime(h1.iloc[1]['dt'], unit='s'))

        df2 = pd.concat([df2, h1], axis=0, ignore_index=True)

    df2['timestamp'] = pd.to_datetime(df2['dt'], unit='s')
    df2.timestamp = df2.timestamp.dt.tz_localize('UTC')
    df2.drop(['dt'], inplace=True, axis=1)
    # df2['precipitation'] = df2['rain_1h'].fillna(0) + df2['snow_1h'].fillna(0)
    df2.drop(['rain_1h'], inplace=True, axis=1)
    df2.drop(['snow_1h'], inplace=True, axis=1)
    df2.reindex(['timestamp', 'temp', 'pressure', 'humidity', 'dew_point', 'uvi', 'clouds',
                 'visibility',
                 'wind_speed', 'wind_deg',
                 'wind_gust'])
    df2.set_index('timestamp', inplace=True)
    df2 = df2[~df2.index.duplicated(keep='first')]
    df2.to_csv('old2.csv')
    if save_to_db and not df.empty:
        save_df_to_database(df=df2, table_name="openweather_old")
