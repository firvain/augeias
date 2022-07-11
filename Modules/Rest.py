import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.errors
import pytz
from dotenv import load_dotenv
from sqlalchemy import create_engine
import json
from flask import Flask, request, jsonify

# Use load_env to trace the path of .env:
load_dotenv('.env')
db_url = os.environ.get("POSTGRESQL_URL")

my_timezone = pytz.timezone('Europe/Athens')
# start flask app
app = Flask(__name__)


def read_sql_data(table_name, local=False):
    engine = create_engine(db_url)

    table_df = pd.read_sql_table(
        table_name,
        con=engine
    )
    if local:
        table_df['timestamp_local'] = table_df['timestamp'].dt.tz_convert(my_timezone)
    table_df.columns.values[0] = 'timestamp'
    table_df.columns.values[1] = 'pyranometer'
    table_df.columns.values[2] = 'precipitation'
    table_df.columns.values[3] = 'temperature'
    table_df.columns.values[4] = 'wind_speed'
    print(table_df.columns)
    return table_df


@app.route("/api/v1/sensors", methods=['GET'])
def test():
    table_name = request.args.get("table")

    return read_sql_data(table_name).head().to_json(orient="records", date_format='iso', force_ascii=False)


app.run(debug=True, port=5000, host="127.0.0.1")
