# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from pandas import notnull, pivot_table, to_numeric

from Modules import Addvantage, Sensors_Mongo
from Utils.Database import save_df_to_database
# Press the green button in the gutter to run the script.
from Utils.Pandas_utils import rename_pandas_columns, resample_dataset, save_pandas_to_csv, save_pandas_to_json

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
    print("working on addvantage")
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

    # Teros_12 -> ok
    print("working on Teros_12")
    m1 = Sensors_Mongo.get_mongo_data('10d60580872b7e0a13ea5b1fe06e36caac95cb0c',
                                      ['soil-bulk-ec0-uS/cm', 'soil-moisture0-%',
                                       'soil-temperature0-C'],
                                      past_hours=PAST_HOURS)
    if not m1.empty:
        m1 = rename_pandas_columns(m1, {'soil-moisture0-%': 'soil-moisture0'})
        m1.dropna(how='all', inplace=True)
        m1_out = resample_dataset(m1)
        save_pandas_to_csv(m1_out, out_path="Data/Sensors", csv_name="teros_12.csv")
        save_pandas_to_json(m1_out, out_path="Data/Sensors", json_name="teros_12.json")
        save_df_to_database(df=m1_out, table_name="teros_12")

    # Triscan -> ok
    print("working on Triscan")
    m2 = Sensors_Mongo.get_mongo_data('1ef55f2a354bd39cca6edb637aec2e0ea55bea09',
                                      ['soil-temperature15-C', 'soil-temperature25-C', 'soil-temperature5-C',
                                       'soil-moisture15-%', 'soil-moisture25-%', 'soil-moisture5-%',
                                       'soil-salinity15-dS/m', 'soil-salinity25-dS/m', 'soil-salinity5-dS/m'],
                                      past_hours=PAST_HOURS)
    if not m2.empty:
        m2 = rename_pandas_columns(m1, {'soil-moisture15-%': "soil-moisture15", 'soil-moisture25-%': 'soil-moisture25',
                                        'soil-moisture5-%': 'soil-moisture5'})
        m2_out = resample_dataset(m2)
        m2_out.dropna(how='all', inplace=True)
        save_pandas_to_csv(m2_out, out_path="Data/Sensors", csv_name="Triscan.csv")
        save_pandas_to_json(m2_out, out_path="Data/Sensors", json_name="Triscan.json")
        save_df_to_database(df=m2_out, table_name="Triscan")

    # Scan_chlori
    print("working on Scan_chlori")
    m3 = Sensors_Mongo.get_mongo_data('218603913b6398d27b0b1612e7ee2e2ee3d036a1',
                                      ['analogInput.2', 'temperatureSensor.1'],

                                      past_hours=PAST_HOURS)
    if not m3.empty:
        m3 = rename_pandas_columns(m3, {'analogInput.2': "chlorine", 'temperatureSensor.1': 'temperatureSensor'})
        m3_out = resample_dataset(m3)
        m3_out.dropna(how='all', inplace=True)
        save_pandas_to_csv(m3_out, out_path="Data/Sensors", csv_name="Scan_chlori.csv")
        save_pandas_to_json(m3_out, out_path="Data/Sensors", json_name="Scan_chlori.json")
        save_df_to_database(df=m3_out, table_name="Scan_chlori")

    # Aquatroll(NDVI) -> ok
    print("working on Aquatroll")
    m4 = Sensors_Mongo.get_mongo_data('323c14d3d8ad3e919ce9699403cbc0ca2ead8c5b',
                                      ['Conductivity0-μS/cm', 'RDO0-mg/l', 'TSS0-mg/l', 'Turbidity0-NTU'],
                                      past_hours=PAST_HOURS)
    if not m4.empty:
        m4_out = resample_dataset(m4)
        m4_out.dropna(how='all', inplace=True)
        save_pandas_to_csv(m4_out, out_path="Data/Sensors", csv_name="Aquatroll.csv")
        save_pandas_to_json(m4_out, out_path="Data/Sensors", json_name="Aquatroll.json")
        save_df_to_database(df=m4_out, table_name="Aquatroll")

    # Proteus_infinite
    print("working on Proteus_infinite")
    m5 = Sensors_Mongo.get_mongo_data('59a85c7da55bf1bf6e784675c060a2e71ee2373a',
                                      ['channel', 'sign', 'value'],
                                      past_hours=PAST_HOURS)
    if not m5.empty:
        m5 = m5.replace('--------', np.nan)
        m5['value'] = to_numeric(m5["value"])
        m5['sign'] = to_numeric(m5["sign"] + str(1))
        m5["value"].apply(lambda x: x * m5['sign'] if notnull(x) else x)
        m5 = pivot_table(m5, values="value", index=['timestamp'], columns=['channel'])
        m5 = m5[m5.columns.intersection(["timestamp", "01", '02', "03", "04", "05", "06", "07", ])]
        m5 = rename_pandas_columns(m5,
                                   {'01': "pH", '02': 'ORP', "03": "total_coli", "04": "BOD", "05": "COD", "06": "NO3",
                                    })

        m5_out = resample_dataset(m5)
        m5_out.dropna(how='all', inplace=True)
        save_pandas_to_csv(m5_out, out_path="Data/Sensors", csv_name="Proteus_infinite.csv")
        save_pandas_to_json(m5_out, out_path="Data/Sensors", json_name="Proteus_infinite.json")
        save_df_to_database(df=m5_out, table_name="Proteus_infinite")

    # ATMOS
    print("working on ATMOS")
    m7 = Sensors_Mongo.get_mongo_data('ff619c613b368b15e14649bd20db7b69c62010fd',
                                      ['air-temperature0-C', 'gust-windspeed0-m/s', 'precipitation0-mm',
                                       'relative-humidity0-%', 'solar-radiation0-W/m2', 'wind-direction0-Degrees',
                                       'windspeed0-m/s', 'timestamp'],
                                      past_hours=PAST_HOURS)
    if not m7.empty:
        m7 = rename_pandas_columns(m7, {'relative-humidity0-%': "relative-humidity0"})
        aggreg = {'air-temperature0-C': "mean", 'gust-windspeed0-m/s': "mean", 'precipitation0-mm': "sum",
                  'relative-humidity0': "mean", 'solar-radiation0-W/m2': "mean",
                  'wind-direction0-Degrees': "mean",
                  'windspeed0-m/s': "mean"}
        m7_out = resample_dataset(m7, aggreg=aggreg)
        m7_out.dropna(how='all', inplace=True)
        save_pandas_to_csv(m7_out, out_path="Data/Sensors", csv_name="ATMOS.csv")
        save_pandas_to_json(m7_out, out_path="Data/Sensors", json_name="ATMOS.json")
        save_df_to_database(df=m7_out, table_name="ATMOS")

    # Rest.test()
