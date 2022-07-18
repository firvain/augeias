import json
import os
from datetime import datetime, timedelta

import pytz
import requests
import xmltodict
from dotenv import load_dotenv
from pandas import DataFrame, to_datetime, set_option
import pymongo
from bson.json_util import dumps

# Use load_env to trace the path of .env:
load_dotenv('.env')
mongo_url = os.environ.get("MONGO_DB")

base_url = "http://scient.static.otenet.gr:82/addUPI?"
hours = 24
slots = int(hours * 60 / 5)

# get datetime
# current_datetime = datetime.now()
current_datetime = to_datetime('today').normalize()
current_minus = current_datetime - timedelta(hours=hours)
before_datetime = current_minus.replace(microsecond=0)

my_timezone = pytz.timezone('Europe/Athens')


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


def get_addvantage_data(session_id, sensor_id):
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
    print(json_WWTP["measurements"])
    json_data = json.dumps(json_WWTP)

    dicti = json.loads(json_data)

    qa = {'time': []}
    for i in dicti['measurements']:
        qa[i] = []
        for idx, item in enumerate(dicti['measurements'][i]):
            if idx == 0:
                item['time'] = datetime.strptime(item["time"], "%Y%m%dT%H:%M:%S")
                item['time'] = my_timezone.localize(item['time'])

            else:

                item["time"] = dicti['measurements'][i][idx - 1]["time"] + timedelta(seconds=int(item["time"][1:]))

            qa['time'].append(item['time'].isoformat())

            qa[i].append(item['value'])

    qa['time'] = sorted(set(qa['time']))
    print(qa)
    df = DataFrame.from_dict(qa)

    df["time"] = to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%S')
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    print(df.describe())
    return df


def get_new_addvantage_data():
    session_id = get_addvantage_session_id()
    data = get_addvantage_data(session_id, sensor_id=7608)
    logout_addvantage(session_id)
    return data
