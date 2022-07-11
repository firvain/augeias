import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import StrMethodFormatter


# fig, ax = plt.subplots()


def vis_data(data_path, file_in, file_out, index, columns=[]):
    data_folder = Path(data_path)
    file_to_open = data_folder / file_in

    df = pd.read_csv(file_to_open)
    print(df['time'])
    # df = df[columns]
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)

    accuracy_cols = [col for col in df.columns if 'accuracy' in col]
    # print(list(df.columns))
    print(accuracy_cols)
    df = df[accuracy_cols]
    print(df.index)
    print('NaN sum', df.isnull().sum().sum())

    df.plot(subplots=True, figsize=(25, 20), grid=True)

    for ax in plt.gcf().axes:
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.4f}'))
    plt.xticks(rotation=90)

    # plt.show()
    plt.savefig(data_folder / file_out)


def compare_dfs(data_path, file1, file2, column):
    data_folder = Path(data_path)
    file1_ = data_folder / file1
    file2_ = data_folder / file2
    df1 = pd.read_csv(file1_, usecols=['time', column])
    df2 = pd.read_csv(file2_, usecols=['time', column])
    df1['time'] = pd.to_datetime(df1['time'])
    df1.set_index('time', inplace=True)
    df2['time'] = pd.to_datetime(df2['time'])
    df2.set_index('time', inplace=True)
    df3 = pd.merge(df1, df2, left_index=True, right_index=True);
    print(df3)
    df4 = pd.concat([df1, df2], axis=1, sort=False).reset_index()
    print(df4)
    df3['diff'] = df3['average_accuracy_x'] - df3['average_accuracy_y']
    print(df3['diff'].describe())
    df3.plot()
    plt.show()
