# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from Modules import Addvantage, Sensors_Mongo, ServerCalls

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Visualize.vis_data('./Data/weather_influx_tables/', 'weather.csv', 'weather.png', 'time',
    #                    ['rain', 'temperature', 'wind_speed'])
    # Visualize.vis_data('./Data/weather_influx_tables/', 'accu_diffs.csv', 'accu_diffs.png', 'time')
    # Visualize.vis_data('./Data/weather_influx_tables/', 'wunder_diffs.csv', 'wunder_diffs.png', 'time')

    # Visualize.compare_dfs('./Data/weather_influx_tables/', 'accu_diffs.csv', 'wunder_diffs.csv', 'average_accuracy')
    # TimeSeriesAnalysis.check_seasonality('./Data/weather_influx_tables/', 'accu_diffs.csv')
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    Addvantage.addvantage("Data/addvantage", "values-addvantage.csv", save_csv=True,
                          csv_name="addvantage.csv", save_to_db=True, db_mode='replace', plot=True)
    new_addvantage_data = ServerCalls.get_new_addvantage_data()
    print(new_addvantage_data.columns)
    print(new_addvantage_data.describe())
    # new_addvantage_data.to_csv('test3.csv')

    # Teros_12 -> ok
    m1 = Sensors_Mongo.get_mongo_data('10d60580872b7e0a13ea5b1fe06e36caac95cb0c',
                                      ['soil-bulk-ec0-uS/cm', 'soil-moisture0-%',
                                       'soil-temperature0-C'],
                                      past_hours=24 * 100)
    print(m1.columns)
    print(m1.describe())
    # Triscan -> ok
    m2 = Sensors_Mongo.get_mongo_data('1ef55f2a354bd39cca6edb637aec2e0ea55bea09',
                                      ['soil-temperature15-C', 'soil-temperature25-C', 'soil-temperature5-C',
                                       'soil-moisture15-%', 'soil-moisture25-%', 'soil-moisture5-%',
                                       'soil-salinity15-dS/m', 'soil-salinity25-dS/m', 'soil-salinity5-dS/m'],
                                      past_hours=24 * 100)
    print(m2.columns)
    print(m2.describe())

    # Scan_chlori
    # m3 = Sensors_Mongo.get_mongo_data('218603913b6398d27b0b1612e7ee2e2ee3d036a1', 'data', past_hours=24 * 100)
    # print(m3.columns)
    # print(m3.describe())

    # NDVI -> ok
    m4 = Sensors_Mongo.get_mongo_data('323c14d3d8ad3e919ce9699403cbc0ca2ead8c5b',
                                      ['ndvi-nir-out0-W/m2',
                                       'ndvi-red-out0-W/m2', 'ndvi0'],
                                      past_hours=24 * 100)
    print(m4.columns)
    print(m4.describe())
    # Proteus_Aquatroll_infinite
    # m5 = Sensors_Mongo.get_mongo_data('59a85c7da55bf1bf6e784675c060a2e71ee2373a', 'ndvi-nir-out0-W/m2',
    #                                 ['ndvi-nir-out0-W/m2',
    #                                  'ndvi-red-out0-W/m2', 'ndvi0'],
    #                                 past_hours=24 * 100)
    # print(m5.columns)
    # print(m5.describe())

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
    # # Rest.test()
