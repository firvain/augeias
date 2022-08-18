import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.errors
import pytz
import requests
import xmltodict
from dotenv import load_dotenv
from pandas import DataFrame, to_datetime
from sqlalchemy import create_engine

# Use load_env to trace the path of .env:
from Utils.Pandas_utils import save_pandas_to_csv, save_pandas_to_json

load_dotenv('.env')
db_url = os.environ.get("POSTGRESQL_URL")
base_url = os.environ.get("ADDVANTAGE_URL")
hours = 24 * 1
slots = int(hours * 60 / 5)
current_datetime = to_datetime('today').normalize()
current_minus = current_datetime - timedelta(hours=hours)
before_datetime = current_minus.replace(microsecond=0)

my_timezone = pytz.timezone('Europe/Athens')


def read_from_csv(file, sep):
    try:
        df = pd.read_csv(file, parse_dates=['Date'], encoding="cp1253", sep=sep)
        final_table_columns = ["Date", "Time", "AIR TEMPERATURE (°C)", "WIND SPEED 100 Hz (m/s)", "Precipitation (mm)",
                               "Pyranometer (W/m²)"]
        df["AIR TEMPERATURE (°C)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
        df["WIND SPEED 100 Hz (m/s)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
        df["Precipitation (mm)"].replace(to_replace=r'\*', value=np.NAN, regex=True, inplace=True)
        df["Pyranometer (W/m²)"].replace(to_replace=r'\*', value=0.0, regex=True, inplace=True)

        df = df[df.columns.intersection(final_table_columns)]
        df['Time'] = pd.to_datetime(df['Time']).dt.time

        # df['timestamp'] = df.apply(lambda r: pd.to_datetime.combine(r['Date'], r['Time']), 1)
        df['timestamp'] = pd.to_datetime(df['Date'].astype(str) + df['Time'].astype(str), format='%Y-%m-%d%H:%M:%S')

        df['timestamp'] = df['timestamp'].dt.tz_localize(my_timezone, ambiguous='infer')

        df.set_index('timestamp', inplace=True)

        out_df = df.drop(labels=['Date', 'Time'], axis=1)
        out_df = out_df.astype(np.float64)
        return out_df
    except pandas.errors.ParserError:
        sys.exit("Parsing file error")


def addvantage_from_csv(in_data_path, file, save_csv=False, out_data_path="", csv_name="", plot=False, save_to_db=True,
                        db_mode='replace',
                        sep=";"):
    in_data_folder = Path(in_data_path)
    in_data_folder.mkdir(parents=True, exist_ok=True)

    if file:
        out_df = read_from_csv(in_data_folder / file, sep)
    else:
        sys.exit("No file")

    if save_to_db:
        try:
            print("saving to db")
            engine = create_engine(db_url)
            out_df.to_sql('addvantage', engine, if_exists=db_mode)
        except ValueError as e:
            sys.exit(e)
    if save_csv:
        save_pandas_to_csv(out_df, out_path=out_data_path, drop_nan=True, csv_name=csv_name)

    if plot:
        data_folder = Path(out_data_path)
        data_folder.mkdir(parents=True, exist_ok=True)
        out_data_folder = Path(out_data_path)
        out_data_folder.mkdir(parents=True, exist_ok=True)
        selected_rows = out_df[~out_df.isnull().any(axis=1)]
        fig, a = plt.subplots(2, 2, figsize=(12, 6), tight_layout=True)
        selected_rows.plot(ax=a, subplots=True, rot=90)
        plt.savefig(out_data_folder / 'addvantage.png')
        plt.show()

    # print(out_df.interpolate().ffill().bfill())


def get_addvantage_session_id():
    response = requests.get(
        f"{base_url}function=login&user=biokoz&passwd=adupi&mode=t&version=1.2")
    obj = xmltodict.parse(response.content)
    return obj["response"]["result"]["string"]


def logout_addvantage(session_id=""):
    response = requests.get(
        f"{base_url}function=logout&session-id={session_id}&mode=t")
    print(response.status_code)


def get_config(session_id):
    response = requests.get(f"{base_url}function=getconfig&session-id={session_id}&id=7608&flags=a&mode=t&df=iso8601")
    obj = xmltodict.parse(response.content)
    print(json.dumps(obj, ensure_ascii=False).encode("utf8").decode())


def get_addvantage_data_from_server(session_id, sensor_id):
    response = requests.get(
        f"{base_url}function=getdata&session-id={session_id}&id={sensor_id}&date={before_datetime.strftime('%Y%m%dT%H:%M:%S')}&slots={slots}&cache=y&mode=t")
    json_dict = xmltodict.parse(response.content)

    json_WWTP = {}
    measurements = {}
    diagnostics = {}
    counter = 0
    jsonDict = {}
    titles = ["Wind speed 100 Hz", "RH", "Air temperature", "Leaf Wetness", "Soil conductivity_25cm",
              "Soil conductivity_15cm", "Soil conductivity_5cm", "Soil temperature_25cm", "Soil temperature_15cm",
              "Soil temperature_5cm", "Soil moisture_25cm", "Soil moisture_15cm", "Soil moisture_5cm", "Precipitation",
              "Pyranometer", "Current of Terminal A", "Relative Humidity Internal", "Data Delay", "GSM Signal Strength",
              "Radio Error Rate (Long-Term)", "Radio Error Rate (Short-Term)", "Temperature Internal",
              "Charging Regulator", "Battery Voltage"]

    for k in range(15):

        if "v" in json_dict["response"]["node"][k]:
            if isinstance(json_dict["response"]["node"][k]["v"], list):
                maxN = len(json_dict["response"]["node"][k]["v"])

                json_object = [{} for x in range(maxN)]
                for i in json_dict["response"]["node"][k]["v"]:
                    json_object[counter]['value'] = i['#text']
                    json_object[counter]['time'] = i['@t']
                    counter = counter + 1
                measurements[titles[k]] = json_object
                counter = 0
            else:
                jsonDict['time'] = json_dict["response"]["node"][k]["v"]["@t"]
                jsonDict['value'] = json_dict["response"]["node"][k]["v"]["#text"]
                measurements[titles[k]] = jsonDict
        else:
            measurements[titles[k]] = json_dict["response"]["node"][k]["error"]["@msg"]

    for k in range(15, 24):
        if "v" in json_dict["response"]["node"][k]:
            if isinstance(json_dict["response"]["node"][k]["v"], list):
                maxN = len(json_dict["response"]["node"][k]["v"])
                json_object = [{} for x in range(maxN)]
                for i in json_dict["response"]["node"][k]["v"]:
                    json_object[counter]['value'] = i['#text']
                    json_object[counter]['time'] = i['@t']
                    counter = counter + 1
                diagnostics[titles[k]] = json_object
                counter = 0
            else:
                jsonDict['time'] = json_dict["response"]["node"][k]["v"]["@t"]
                jsonDict['value'] = json_dict["response"]["node"][k]["v"]["#text"]
                diagnostics[titles[k]] = jsonDict
        else:
            diagnostics[titles[k]] = json_dict["response"]["node"][k]["error"]["@msg"]

    json_WWTP["measurements"] = measurements
    json_WWTP["diagnostics"] = diagnostics
    # print(json_WWTP["measurements"])
    json_data = json.dumps(json_WWTP)

    dicti = json.loads(json_data)

    qa = {'timestamp': []}
    for i in dicti['measurements']:
        qa[i] = []
        for idx, item in enumerate(dicti['measurements'][i]):
            if idx == 0:
                item['time'] = datetime.strptime(item["time"], "%Y%m%dT%H:%M:%S")
                item['time'] = my_timezone.localize(item['time'])

            else:

                item["time"] = dicti['measurements'][i][idx - 1]["time"] + timedelta(seconds=int(item["time"][1:]))

            qa['timestamp'].append(item['time'].isoformat())

            qa[i].append(item['value'])

    qa['timestamp'] = sorted(set(qa['timestamp']))
    # print(qa)
    df = DataFrame.from_dict(qa)

    df["timestamp"] = to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    # print(df.columns.tolist())
    return df.apply(pd.to_numeric)


def get_new_addvantage_data(save_csv=False, out_data_path="", csv_name="", save_json=False, json_name="", aggreg={}):
    session_id = get_addvantage_session_id()
    data = get_addvantage_data_from_server(session_id, sensor_id=7608)
    logout_addvantage(session_id)

    if save_csv:
        save_pandas_to_csv(data, out_path=out_data_path, drop_nan=True, csv_name=csv_name, aggreg=aggreg)
    if save_json:
        save_pandas_to_json(data, out_path=out_data_path, drop_nan=True, json_name=json_name, aggreg=aggreg)

    return data
