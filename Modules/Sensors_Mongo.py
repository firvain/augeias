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


def get_users_collections(past_hours: int = 24):
    client = pymongo.MongoClient(mongo_url)
    db = client['resources']
    for user in db['users'].find({}):
        user_id = user.get("_id")
        for application_group in db["application_groups"].find({"user_id": {"$eq": user_id}}):
            # print(application_group)
            application_group_id = application_group.get("_id")
            # print(application_group_id)
            for user_application in db["applications"].find({"application_group_id": {"$eq": application_group_id}}):

                collection = user_application.get("raw_storage_id")
                db = client['payloads']
                if collection:
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
                            js["user_id"] = user_id
                            js["application_group_id"] = application_group_id

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
                        yield df
                        # return df[df.columns.intersection(key_list)]


def get_mongo_data2(collection, key_list=[], key_list2=[], past_hours=24):
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
    app_id = ''
    for x in col.find().sort('_id', -1).limit(1):
        app_id = x.get("app_id")
    print(app_id)
    db2 = client["resources"]
    application_group_id = db2['applications'].find_one({"_id": {"$eq": app_id}}).get("application_group_id")

    for x in col.find({"arrived_at": {"$gt": today - timedelta(hours=past_hours)}}):

        try:
            js = json.loads(x.get('payload')['objectJSON'])
            # print(js.keys())
            js["timestamp"] = x.get("arrived_at")
            js["application_group_id"] = application_group_id
            # print(js)
            for key in js.keys():
                if not js.get(key) is None:
                    # print(js)
                    json_data_list.append(js)
        except (KeyError, json.JSONDecodeError, TypeError):
            # print(e)
            pass

    df = DataFrame(json_normalize(json_data_list, max_level=1))
    print(json_data_list)
    quit()
    if not df.empty:
        df.set_index("timestamp", inplace=True)

        df.index = df.index.tz_localize(pytz.utc)
        # set_option('display.max_columns', None)
        df = df[~df.index.duplicated(keep='last')]

        return df[df.columns.intersection(key_list.append('application_group_id'))]
        # if df.isnull().values.any():
        #     print('interpolating')
        #     int_df = df.interpolate().ffill().bfill()
        #     data = int_df[int_df.columns.intersection(key_list)]
        #     return data
        # else:
        #     data = df[df.columns.intersection(key_list)]
        #     return data


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
