import json
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from pandas import DataFrame
import pymongo

# Use load_env to trace the path of .env:
from pandas import json_normalize
from colorama import Fore
from colorama import init

init(autoreset=True)
load_dotenv('.env')
mongo_url = os.environ.get("MONGO_DB")


def get_mongo_data(collection, key_list=[], key_list2=[], past_hours=24):
    print(f"connecting to collection {Fore.CYAN}{collection}")
    print(f'{Fore.BLUE}mongo_url {mongo_url}')

    client = pymongo.MongoClient(mongo_url)

    db = client['payloads']
    col = db[collection]
    today = datetime.utcnow()
    print(f"today is {Fore.CYAN}{today}")
    back = today - timedelta(hours=past_hours)
    print(f'start at {Fore.LIGHTMAGENTA_EX} {back}')
    json_data_list = []
    for x in col.find({"arrived_at": {"$gt": today - timedelta(hours=past_hours)}}):
        try:
            js = json.loads(x.get('payload')['objectJSON'])
            # print(js.keys())
            js["timestamp"] = x.get("arrived_at")
            # print(js)
            for key in js.keys():
                if not js.get(key) is None:
                    # print(js)
                    json_data_list.append(js)
        except (KeyError, json.JSONDecodeError, TypeError):
            # print(e)
            pass

    df = DataFrame(json_normalize(json_data_list, max_level=1))
    # print(json_data_list)
    if not df.empty:
        df.set_index("timestamp", inplace=True)

        df.index = df.index.tz_localize(pytz.utc)
        # set_option('display.max_columns', None)
        df = df[~df.index.duplicated(keep='last')]
        return df[df.columns.intersection(key_list)]
        # if df.isnull().values.any():
        #     print('interpolating')
        #     int_df = df.interpolate().ffill().bfill()
        #     data = int_df[int_df.columns.intersection(key_list)]
        #     return data
        # else:
        #     data = df[df.columns.intersection(key_list)]
        #     return data


def get_mongo_datα_minutely(collection, key_list=[], key_list2=[], past_minutes=15):
    print(f"connecting to collection {Fore.CYAN}{collection}")
    print(f'{Fore.BLUE}mongo_url {mongo_url}')

    client = pymongo.MongoClient(mongo_url)

    db = client['payloads']
    col = db[collection]
    today = datetime.utcnow()
    print(f"today is {Fore.CYAN}{today}")
    back = today - timedelta(minutes=past_minutes)
    print(f'start at {Fore.LIGHTMAGENTA_EX} {back}')
    json_data_list = []
    for x in col.find({"arrived_at": {"$gt": today - timedelta(minutes=past_minutes)}}):

        try:
            js = json.loads(x.get('payload')['objectJSON'])
            # print(js.keys())
            js["timestamp"] = x.get("arrived_at")
            # print(js)
            for key in js.keys():
                if not js.get(key) is None:
                    # print(js)
                    json_data_list.append(js)
        except (KeyError, json.JSONDecodeError, TypeError):
            # print(e)
            pass

    df = DataFrame(json_normalize(json_data_list, max_level=1))
    # print(json_data_list)
    if not df.empty:
        df.set_index("timestamp", inplace=True)

        df.index = df.index.tz_localize(pytz.utc)
        # set_option('display.max_columns', None)
        df = df[~df.index.duplicated(keep='last')]
        return df[df.columns.intersection(key_list)]
        # if df.isnull().values.any():
        #     print('interpolating')
        #     int_df = df.interpolate().ffill().bfill()
        #     data = int_df[int_df.columns.intersection(key_list)]
        #     return data
        # else:
        #     data = df[df.columns.intersection(key_list)]
        #     return data
