# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from Modules import Addvantage, ServerCalls

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Visualize.vis_data('./Data/weather_influx_tables/', 'weather.csv', 'weather.png', 'time',
    #                    ['rain', 'temperature', 'wind_speed'])
    # Visualize.vis_data('./Data/weather_influx_tables/', 'accu_diffs.csv', 'accu_diffs.png', 'time')
    # Visualize.vis_data('./Data/weather_influx_tables/', 'wunder_diffs.csv', 'wunder_diffs.png', 'time')

    # Visualize.compare_dfs('./Data/weather_influx_tables/', 'accu_diffs.csv', 'wunder_diffs.csv', 'average_accuracy')
    # TimeSeriesAnalysis.check_seasonality('./Data/weather_influx_tables/', 'accu_diffs.csv')
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    # Addvantage.addvantage("Data/addvantage", "values-addvantage.csv", save_csv=True,
    #                       csv_name="addvantage.csv", save_to_db=True, db_mode='replace', plot=True)
    new_addvantage_data = ServerCalls.get_new_addvantage_data()
    new_addvantage_data.to_csv('test3.csv')
    # Rest.test()
