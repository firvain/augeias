# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from pandas import notnull, pivot_table, to_numeric

from Modules import Addvantage, Sensors_Mongo
# Press the green button in the gutter to run the script.
from Utils.Pandas_utils import rename_pandas_columns, save_pandas_to_csv, save_pandas_to_json

PAST_DAYS = 1
PAST_HOURS = 24 * PAST_DAYS
if __name__ == '__main__':
    # Visualize.vis_data('./Data/weather_influx_tables/', 'weather.csv', 'weather.png', 'time',
    #                    ['rain', 'temperature', 'wind_speed'])
    # Visualize.vis_data('./Data/weather_influx_tables/', 'accu_diffs.csv', 'accu_diffs.png', 'time')
    # Visualize.vis_data('./Data/weather_influx_tables/', 'wunder_diffs.csv', 'wunder_diffs.png', 'time')

    # Visualize.compare_dfs('./Data/weather_influx_tables/', 'accu_diffs.csv', 'wunder_diffs.csv', 'average_accuracy')
    # TimeSeriesAnalysis.check_seasonality('./Data/weather_influx_tables/', 'accu_diffs.csv')
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    # Addvantage -> ok
    # Addvantage.addvantage_from_csv("Data/addvantage", "values-addvantage.csv", save_csv=True,
    #                                out_data_path="Data/addvantage/result",
    #                                csv_name="addvantage.csv", save_to_db=False, db_mode='replace', plot=True)
    #
    Addvantage.get_new_addvantage_data(save_csv=True, out_data_path="Data/addvantage/result",
                                       csv_name="new_ADDvantage_data.csv", save_json=True,
                                       json_name="new_ADDvantage_data.json",
                                       aggreg={'Wind speed 100 Hz': "mean", 'RH': "mean", 'Air temperature': "mean",
                                               'Leaf Wetness': "mean", 'Soil conductivity_25cm': "mean",
                                               'Soil conductivity_15cm': "mean", 'Soil conductivity_5cm': "mean",
                                               'Soil temperature_25cm': "mean", 'Soil temperature_15cm': "mean",
                                               'Soil temperature_5cm': "mean", 'Soil moisture_25cm': "mean",
                                               'Soil moisture_15cm': "mean", 'Soil moisture_5cm': "mean",
                                               'Precipitation': "sum", 'Pyranometer': "mean"
                                               })

    # # Teros_12 -> ok
    m1 = Sensors_Mongo.get_mongo_data('10d60580872b7e0a13ea5b1fe06e36caac95cb0c',
                                      ['soil-bulk-ec0-uS/cm', 'soil-moisture0-%',
                                       'soil-temperature0-C'],
                                      past_hours=PAST_HOURS)
    print(m1.columns)
    print(m1.describe())
    save_pandas_to_csv(m1, out_path="Data/Sensors", drop_nan=True, csv_name="Teros_12.csv")
    save_pandas_to_json(m1, out_path="Data/Sensors", drop_nan=True, json_name="Teros_12.json")

    #
    # # Triscan -> ok
    m2 = Sensors_Mongo.get_mongo_data('1ef55f2a354bd39cca6edb637aec2e0ea55bea09',
                                      ['soil-temperature15-C', 'soil-temperature25-C', 'soil-temperature5-C',
                                       'soil-moisture15-%', 'soil-moisture25-%', 'soil-moisture5-%',
                                       'soil-salinity15-dS/m', 'soil-salinity25-dS/m', 'soil-salinity5-dS/m'],
                                      past_hours=PAST_HOURS)
    print(m2.columns)
    print(m2.describe())
    save_pandas_to_csv(m2, out_path="Data/Sensors", drop_nan=True, csv_name="Triscan.csv")
    save_pandas_to_json(m2, out_path="Data/Sensors", drop_nan=True, json_name="Triscan.json")
    #
    # # Scan_chlori
    m3 = Sensors_Mongo.get_mongo_data('218603913b6398d27b0b1612e7ee2e2ee3d036a1',
                                      ['analogInput.2', 'temperatureSensor.1'],

                                      past_hours=PAST_HOURS)
    print(m3.columns)
    print(m3.describe())
    m3 = rename_pandas_columns(m3, {'analogInput.2': "chlorine", 'temperatureSensor.1': 'temperatureSensor'})
    save_pandas_to_csv(m3, out_path="Data/Sensors", drop_nan=True, csv_name="Scan_chlori.csv")
    save_pandas_to_json(m3, out_path="Data/Sensors", drop_nan=True, json_name="Scan_chlori.json")
    #
    # # Aquatroll(NDVI) -> ok
    m4 = Sensors_Mongo.get_mongo_data('323c14d3d8ad3e919ce9699403cbc0ca2ead8c5b',
                                      ['Conductivity0-μS/cm', 'RDO0-mg/l', 'TSS0-mg/l', 'Turbidity0-NTU'],
                                      past_hours=PAST_HOURS)
    print(m4.columns)
    print(m4.describe())

    save_pandas_to_csv(m4, out_path="Data/Sensors", drop_nan=True, csv_name="Aquatroll.csv")
    save_pandas_to_json(m4, out_path="Data/Sensors", drop_nan=False, json_name="Aquatroll.json")

    # Proteus_infinite
    m5 = Sensors_Mongo.get_mongo_data('59a85c7da55bf1bf6e784675c060a2e71ee2373a',
                                      ['channel', 'sign', 'value'],
                                      past_hours=PAST_HOURS)

    m5 = m5.replace('--------', np.nan)
    m5['value'] = to_numeric(m5["value"])
    m5['sign'] = to_numeric(m5["sign"] + str(1))
    m5["value"].apply(lambda x: x * m5['sign'] if notnull(x) else x)
    m5 = pivot_table(m5, values="value", index=['timestamp'], columns=['channel'])
    m5 = m5[m5.columns.intersection(["timestamp", "01", '02', "03", "04", "05", "06", "07", ])]
    m5 = rename_pandas_columns(m5, {'01': "pH", '02': 'ORP', "03": "total_coli", "04": "BOD", "05": "COD", "06": "NO3",
                                    })
    print(m5.describe())
    save_pandas_to_csv(m5, out_path="Data/Sensors", drop_nan=True, csv_name="Proteus_infinite.csv")
    save_pandas_to_json(m5, out_path="Data/Sensors", drop_nan=True, json_name="Proteus_infinite.json")

    # ATMOS
    m7 = Sensors_Mongo.get_mongo_data('ff619c613b368b15e14649bd20db7b69c62010fd',
                                      ['air-temperature0-C', 'gust-windspeed0-m/s', 'precipitation0-mm',
                                       'relative-humidity0-%', 'solar-radiation0-W/m2', 'wind-direction0-Degrees',
                                       'windspeed0-m/s', 'timestamp'],
                                      past_hours=PAST_HOURS)
    print(m7.columns)
    print(m7.describe())

    save_pandas_to_csv(m7, out_path="Data/Sensors", drop_nan=True, csv_name="ATMOS.csv",
                       aggreg={'air-temperature0-C': "mean", 'gust-windspeed0-m/s': "mean", 'precipitation0-mm': "sum",
                               'relative-humidity0-%': "mean", 'solar-radiation0-W/m2': "mean",
                               'wind-direction0-Degrees': "mean",
                               'windspeed0-m/s': "mean"})
    save_pandas_to_json(m7, out_path="Data/Sensors", drop_nan=True, json_name="ATMOS.json")
    # Rest.test()
