# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np

from pandas import notnull, pivot_table, to_numeric
from pathlib import Path
from Modules import Addvantage, Sensors_Mongo
# Press the green button in the gutter to run the script.
from Modules.Utils import rename_pandas_columns

sensors_folder = Path('Data/Sensors')
sensors_folder.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    # Visualize.vis_data('./Data/weather_influx_tables/', 'weather.csv', 'weather.png', 'time',
    #                    ['rain', 'temperature', 'wind_speed'])
    # Visualize.vis_data('./Data/weather_influx_tables/', 'accu_diffs.csv', 'accu_diffs.png', 'time')
    # Visualize.vis_data('./Data/weather_influx_tables/', 'wunder_diffs.csv', 'wunder_diffs.png', 'time')

    # Visualize.compare_dfs('./Data/weather_influx_tables/', 'accu_diffs.csv', 'wunder_diffs.csv', 'average_accuracy')
    # TimeSeriesAnalysis.check_seasonality('./Data/weather_influx_tables/', 'accu_diffs.csv')
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
    # Addvantage -> ok
    Addvantage.addvantage_from_csv("Data/addvantage", "values-addvantage.csv", save_csv=True,
                                   out_data_path="Data/addvantage/result",
                                   csv_name="addvantage.csv", save_to_db=False, db_mode='replace', plot=True)

    Addvantage.get_new_addvantage_data(save_csv=True, out_data_path="Data/addvantage/result",
                                       csv_name="new_addvantage_data.csv")

    # Teros_12 -> ok
    m1 = Sensors_Mongo.get_mongo_data('10d60580872b7e0a13ea5b1fe06e36caac95cb0c',
                                      ['soil-bulk-ec0-uS/cm', 'soil-moisture0-%',
                                       'soil-temperature0-C'],
                                      past_hours=24 * 100)
    print(m1.columns)
    print(m1.describe())
    m1.dropna(how='all').to_csv(sensors_folder / "Teros_12.csv")

    # Triscan -> ok
    m2 = Sensors_Mongo.get_mongo_data('1ef55f2a354bd39cca6edb637aec2e0ea55bea09',
                                      ['soil-temperature15-C', 'soil-temperature25-C', 'soil-temperature5-C',
                                       'soil-moisture15-%', 'soil-moisture25-%', 'soil-moisture5-%',
                                       'soil-salinity15-dS/m', 'soil-salinity25-dS/m', 'soil-salinity5-dS/m'],
                                      past_hours=24 * 100)
    print(m2.columns)
    print(m2.describe())

    m1.dropna(how='all').to_csv(sensors_folder / "Triscan.csv")

    # Scan_chlori
    m3 = Sensors_Mongo.get_mongo_data('218603913b6398d27b0b1612e7ee2e2ee3d036a1',
                                      ['analogInput.2', 'temperatureSensor.1'],

                                      past_hours=24 * 100)
    print(m3.columns)
    print(m3.describe())
    m3 = rename_pandas_columns(m3, {'analogInput.2': "analogInput", 'temperatureSensor.1': 'temperatureSensor'})
    m3.dropna(how='all').to_csv(sensors_folder / "Scan_chlori.csv")

    # NDVI -> ok
    m4 = Sensors_Mongo.get_mongo_data('323c14d3d8ad3e919ce9699403cbc0ca2ead8c5b',
                                      ['ndvi-nir-out0-W/m2',
                                       'ndvi-red-out0-W/m2', 'ndvi0'],
                                      past_hours=24 * 100)
    print(m4.columns)
    print(m4.describe())
    m4.dropna(how='all').to_csv(sensors_folder / "NDVI.csv")

    # Proteus_Aquatroll_infinite
    m5 = Sensors_Mongo.get_mongo_data('59a85c7da55bf1bf6e784675c060a2e71ee2373a',
                                      ['channel', 'sign', 'value'],
                                      past_hours=24 * 10)

    m5 = m5.replace('--------', np.nan)
    m5['value'] = to_numeric(m5["value"])
    m5['sign'] = to_numeric(m5["sign"] + str(1))
    m5["value"].apply(lambda x: x * m5['sign'] if notnull(x) else x)
    m5 = pivot_table(m5, values="value", index=['timestamp'], columns=['channel'])
    m5 = m5[m5.columns.intersection(["timestamp", "01", '02', "03", "04", "05", "06", "07", ])]
    m5 = rename_pandas_columns(m5, {'01': "pH", '02': 'ORP', "03": "total_coli", "04": "BOD", "05": "COD", "06": "NO3",
                                    "07": "temperature"})
    print(m5.describe())

    m5.dropna(how='all').to_csv(sensors_folder / "Proteus_Aquatroll_infinite.csv")

    # delta_Ohm_chlori
    # m6 = Sensors_Mongo.get_mongo_data('5a34df56477c024587592a8e1fe3a768f1929b10', 'temperatureSensor',
    #                                 ["temperatureSensor"],
    #                                 past_hours=24 * 100)
    # print(m6.columns)
    # print(m6.describe())

    # ATMOS
    m7 = Sensors_Mongo.get_mongo_data('ff619c613b368b15e14649bd20db7b69c62010fd',
                                      ['air-temperature0-C', 'gust-windspeed0-m/s', 'precipitation0-mm',
                                       'relative-humidity0-%', 'solar-radiation0-W/m2', 'wind-direction0-Degrees',
                                       'windspeed0-m/s', 'timestamp'],
                                      past_hours=24 * 100)
    print(m7.columns)
    print(m7.describe())
    m7.dropna(how='all').to_csv(sensors_folder / "ATMOS.csv")

    # # Rest.test()
