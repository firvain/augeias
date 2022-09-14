from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import tensorflow as tf
from keras.callbacks import EarlyStopping
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
from pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
import seaborn as sns
from Utils.Database import get_data_from_augeias_postgresql

register_matplotlib_converters()
sns.set(style='whitegrid', palette='muted', font_scale=1.5)
rcParams['figure.figsize'] = 22, 10

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


# gdown.download(url='https://drive.google.com/uc?id=10vdMg_RazoIatwrT7azKFX4P02OebU76', output='spx.csv')
# df = get_data_from_augeias_postgresql('Teros_12')
# engine = create_engine('postgresql://augeias:augeias@83.212.19.17:5432/augeias')
def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)


def detect_anomalies_lstm(table_name: str, TIME_STEPS: int = 24, out_path: str = 'Data/Sensors/Anomalies',
                          train_model: bool = True):
    out_folder = Path(f'{out_path}/{table_name}')
    out_folder.mkdir(parents=True, exist_ok=True)
    data = get_data_from_augeias_postgresql(table_name)
    if isinstance(data, pd.DataFrame) and not data.empty:
        data.dropna(inplace=True)

        cols = data.columns.tolist()

        for i, column in enumerate(cols):

            print(f'Working on column: {column}')
            print(f'Time steps: {TIME_STEPS}')
            df = data[[column]].copy()

            # THRESHOLD = df[column].quantile(0.01)

            # print(len(df))
            # print(len(df) % TIME_STEPS)
            # print(len(df) - (len(df) % TIME_STEPS))
            # start_time = df.index[0]
            # e = start_time + timedelta(days=1)
            # print(start_time)
            # print(24 - start_time.hour)
            # print(e - start_time)
            #
            # print(datetime.strptime('2022-05-21', '%Y-%m-%d %H:%M'))
            # res = df[~(df.index < '2022-05-21']
            # # print(res)
            train_size = int(len(df) - 24)
            # print(train_size)
            # test_size = len(df) - train_size
            train, test = df.iloc[0:train_size], df.iloc[train_size:(len(df))]
            # print(f'train.shape: {train.shape}, test.shape: {test.shape}')
            # print(train.head())

            scaler = MinMaxScaler()
            scaler = scaler.fit(train[[column]])

            train[column] = scaler.transform(train[[column]])
            test[column] = scaler.transform(test[[column]])

            # THRESHOLD = scaler.transform(
            #     pd.Series(data={'threshold': THRESHOLD}, index=['threshold']).values.reshape(1, -1))[0]
            # print(f'test.shape{test.shape}')
            #
            # q = scaler.inverse_transform(THRESHOLD.reshape(-1, 1)).reshape(-1)
            # THRESHOLD = abs(THRESHOLD[0])

            X_train, y_train = create_dataset(train[[column]], train[column], TIME_STEPS)
            X_test, y_test = create_dataset(test[[column]], test[column], TIME_STEPS)

            print(f'Training shape: {X_train.shape}')
            print(f'Testing shape: {X_test.shape}')

            if train_model:
                model = keras.Sequential()
                model.add(keras.layers.LSTM(
                    units=64,
                    input_shape=(X_train.shape[1], X_train.shape[2])
                ))
                model.add(keras.layers.Dropout(rate=0.3))
                model.add(keras.layers.RepeatVector(n=X_train.shape[1]))
                model.add(keras.layers.LSTM(units=64, return_sequences=True))
                model.add(keras.layers.Dropout(rate=0.3))
                model.add(keras.layers.TimeDistributed(keras.layers.Dense(units=X_train.shape[2])))
                model.compile(loss='mae', optimizer='adam')

                es = EarlyStopping(monitor='val_loss', mode='min', patience=10)
                print(model.summary())
                history = model.fit(
                    X_train, y_train,
                    epochs=100,
                    batch_size=32,
                    validation_split=0.2,
                    shuffle=False,
                    callbacks=[es],
                )
                print('Model Evaluation', model.evaluate(X_test, y_test))
                model.save(out_folder / f'{table_name}_{column}_model.h5')

            else:
                model = keras.models.load_model(out_folder / f'{table_name}_{column}_model.h5')
                es = EarlyStopping(monitor='val_loss', mode='min', patience=10)
                # history = model.fit(
                #     X_train, y_train,
                #     epochs=100,
                #     batch_size=32,
                #     validation_split=0.2,
                #     shuffle=False,
                #     callbacks=[es],
                # )
            # plt.plot(history.history['loss'], label='train')
            # plt.plot(history.history['val_loss'], label='test')
            # plt.legend()
            # plt.show()

            X_train_pred = model.predict(X_train)
            train_mae_loss = np.mean(np.abs(X_train_pred - X_train), axis=1)
            # plt.hist(train_mae_loss, bins=50)
            # plt.xlabel('Train MAE loss')
            # plt.ylabel('Number of Samples');
            # plt.show()
            threshold = np.max(train_mae_loss)
            print(f'Reconstruction error threshold: {threshold}')

            X_test_pred = model.predict(X_test)
            test_mae_loss = np.mean(np.abs(X_test_pred - X_test), axis=1)
            # plt.hist(test_mae_loss, bins=50)
            # plt.xlabel('Test MAE loss')
            # plt.ylabel('Number of samples');
            # plt.show()

            test_score_df = pd.DataFrame(test[TIME_STEPS:])

            test_score_df['loss'] = test_mae_loss
            test_score_df['threshold'] = threshold
            test_score_df['anomaly'] = test_score_df.loss > test_score_df.threshold
            test_score_df[column] = test[TIME_STEPS:][column]

            print(test_score_df)

            anomalies = test_score_df.loc[test_score_df['anomaly'] == True]
            print(f'anomalies shape: {anomalies.shape}')

            if not anomalies.empty:
                yhat = scaler.inverse_transform(anomalies[column].values.reshape(-1, 1)).reshape(-1)
                # fig = go.Figure()
                # fig.add_trace(go.Scatter(x=test_score_df.index,
                #                          y=scaler.inverse_transform(
                #                              test_score_df[column].values.reshape(-1, 1)).reshape(-1),
                #                          name=column))
                # fig.add_trace(
                #     go.Scatter(x=anomalies.index, y=yhat, mode='markers',
                #                name='Anomaly'))
                # fig.update_layout(showlegend=True, title='Detected anomalies')
                # fig.show()
                plt.plot(
                    test[TIME_STEPS:].index,
                    scaler.inverse_transform(test[TIME_STEPS:][column].values.reshape(-1, 1)).reshape(-1),
                    label=f'{column}'
                )

                sns.scatterplot(
                    anomalies.index,
                    yhat,
                    color=sns.color_palette()[3],
                    s=52,
                    label='anomaly'
                )
                plt.xticks(rotation=25)
                plt.legend()
                plt.title(f'{table_name} - Anomalies')
                plt.show()
            else:
                yhat = 0
                print(f'No anomalies found with THRESHOLD: {threshold}')
            anomalies[column] = yhat

            anomalies.to_csv(out_folder / f'LSTM_anomalies_{column}_{table_name}.csv')
