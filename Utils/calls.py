import requests

BASE_URL = 'http://34.241.87.71:8081/'
POST_API_KEY = 'AC8tQF4YAqgne8G90PVlWKxUv48veTmpsYOyHUfMpQDRXlkhlJ9Alsp7nzIKd5Dghumy7fTFheCAVggc3MqFbo90h31Uv81bn6XgxLzCMh70lIuXoiRs591HR1ynrKKj'


def push_to_aws(df, table_name: str):
    print(table_name)
    data = df.copy().reset_index()

    data['timestamp'] = data['timestamp'].astype(str)

    url = f'{BASE_URL}{table_name}'
    print(data.to_json(orient='records'))

    return requests.post(headers={'apikey': POST_API_KEY},
                         url=url, data=data.to_json(orient='records'))


def push_to_aws_last_row(df, table_name: str):
    data = df.copy().reset_index()
    data['timestamp'] = data['timestamp'].astype(str)

    url = f'{BASE_URL}{table_name}'

    return requests.post(headers={'apikey': POST_API_KEY},
                         url=url, data=data.iloc[-1].to_json())
