import json
import os
from datetime import datetime

import pandas as pd
import pytz
import requests
from colorama import init
from dotenv import load_dotenv

from Utils.Database import save_df_to_database

# create a new empty instance

init(autoreset=True)
load_dotenv('.env')

api_key = os.environ.get("ACCUWEATHER_API_KEY")


class Hasher(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def get_accuweather_daily(save_to_db: bool = True):
    url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/184896?apikey={api_key}&details=true&metric=true'

    print(url)
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        # with open('json_data.json', 'r') as fcc_file:
        #     data = json.load(fcc_file)
        #     print(data)
        with open('json_data.json', 'w') as outfile:
            json.dump(data, outfile)

        # if data.get("Code") is not None:
        #     raise Exception(data.get("Message"))

        # out_data = np.empty(shape=(11, len(data['hourly'])))
        my_list = []
        for entry in data:
            dt = datetime.fromtimestamp(entry["EpochDateTime"], pytz.UTC)

            temp = entry.get('Temperature', {}).get('Value')

            dew_point = entry.get('DewPoint', {}).get('Value')

            wind_speed = entry.get('Wind', {}).get('Speed', {}).get("Value")

            wind_deg = entry.get('Wind', {}).get('Direction', {}).get("Degrees")
            wind_gust = entry.get('WindGust', {}).get('Speed', {}).get("Value")

            uvi = entry["UVIndex"]

            rh = entry["RelativeHumidity"]

            precipitation = entry.get('TotalLiquid', {}).get("Value")
            rain = entry.get('Rain', {}).get("Value")

            snow = entry.get('Snow', {}).get("Value")
            ice = entry.get('Ice', {}).get("Value")
            clouds = entry['CloudCover']

            solar_irradiance = entry.get('SolarIrradiance', {}).get("Value")
            evapotranspiration = entry.get('Evapotranspiration', {}).get("Value")

            my_list.append([dt, temp, dew_point, wind_speed, wind_deg,
                            wind_gust, uvi, rh, precipitation, rain, snow, ice, clouds, solar_irradiance,
                            evapotranspiration])
        df = pd.DataFrame(my_list,
                          columns=['timestamp', 'temp', 'dew_point', 'wind_speed', 'wind_deg',
                                   'wind_gust', 'uvi', 'rh', 'precipitation', 'rain', 'snow', 'ice', 'clouds',
                                   'solar_irradiance', 'evapotranspiration'])
        df.set_index('timestamp', inplace=True)

        if save_to_db and not df.empty:
            save_df_to_database(df=df, table_name="accuweather_direct")
        else:
            raise Exception('no data returned')
    except Exception as e:
        print(e)
