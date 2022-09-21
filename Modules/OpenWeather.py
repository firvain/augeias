import json
import os
from datetime import datetime

import numpy as np
import pytz
import requests
from colorama import init
from dotenv import load_dotenv
import pandas as pd

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
