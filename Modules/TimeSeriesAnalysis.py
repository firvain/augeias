import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from pathlib import Path


def check_seasonality(data_path, file, column='average_accuracy'):
    data_folder = Path(data_path)
    file_ = data_folder / file
    df = pd.read_csv(file_, usecols=['time', column])
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').resample('D').ffill()
   
    decompose_result_mult = seasonal_decompose(df, model="ad")

    trend = decompose_result_mult.trend
    seasonal = decompose_result_mult.seasonal
    residual = decompose_result_mult.resid

    decompose_result_mult.plot();
    for ax in plt.gcf().axes:
        ax.tick_params(labelrotation=90)
    plt.show()
