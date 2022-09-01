import matplotlib.pyplot as plt
import numpy as np

from sklearn.ensemble import IsolationForest

from Utils.Database import get_data_from_augeias_postgresql

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)


def detect_anomalies(table_name: str):
    df = get_data_from_augeias_postgresql(table_name)
    df.dropna(inplace=True)
    cols = df.columns.tolist()

    fig, axs = plt.subplots(1, len(cols), figsize=(22, 12), facecolor='w', edgecolor='k')

    axs = axs.ravel()
    for i, column in enumerate(cols):
        df.hist(column=column, ax=axs[i])
        # plt.title(f'Histogram of {table_name}')
    plt.savefig(f'Histogram of {table_name}.png')
    fig, axs = plt.subplots(1, len(cols), figsize=(22, 12), facecolor='w', edgecolor='k')

    axs = axs.ravel()
    for i, column in enumerate(cols):
        isolation_forest = IsolationForest(contamination='auto', random_state=42)
        isolation_forest.fit(df[column].values.reshape(-1, 1))

        xx = np.linspace(df[column].min_val(), df[column].max(), len(df)).reshape(-1, 1)
        anomaly_score = isolation_forest.decision_function(xx)
        outlier = isolation_forest.predict(xx)

        axs[i].plot(xx, anomaly_score, label='anomaly score')
        axs[i].fill_between(xx.T[0], np.min(anomaly_score), np.max(anomaly_score),
                            where=outlier == -1, color='r',
                            alpha=.4, label='outlier region')
        axs[i].legend()
        axs[i].set_title(column)
    plt.savefig(f'Anomalies of {table_name.capitalize()}.png')
