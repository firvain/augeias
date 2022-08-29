import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from dotenv import load_dotenv
from keras.callbacks import EarlyStopping
from pandas.plotting import register_matplotlib_converters
# import gdown
from pylab import rcParams
from sqlalchemy import create_engine
from tensorflow import keras
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from Utils.Database import get_data_from_augeias_postgresql

register_matplotlib_converters()
sns.set(style='whitegrid', palette='muted', font_scale=1.5)

rcParams['figure.figsize'] = 22, 10

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# gdown.download(url='https://drive.google.com/uc?id=10vdMg_RazoIatwrT7azKFX4P02OebU76', output='spx.csv')
# df = get_data_from_augeias_postgresql('Teros_12')
engine = create_engine('postgresql://augeias:augeias@83.212.19.17:5432/augeias')
table_name = "Teros_12"
variable_name = 'soil-bulk-ec'
try:
    sql = f"""select timestamp, "{variable_name}" from {table_name}"""
    print(sql)
    data = pd.read_sql(sql, con=engine, index_col="timestamp")
    print(data)

except ValueError as e:
    print(e)
# df = pd.read_csv('spx.csv', parse_dates=['date'], index_col='date')
print(data)

df = data[[variable_name]].copy()
print(df.tail())
# plt.plot(df, label='close price')
# plt.legend()
# plt.show()

train_size = int(len(df) * 0.70)
test_size = len(df) - train_size
train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]
print(f'train.shape: {train.shape}, test.shape: {test.shape}')

scaler = MinMaxScaler()
scaler = scaler.fit(train[[variable_name]])

train[variable_name] = scaler.transform(train[[variable_name]])
test[variable_name] = scaler.transform(test[[variable_name]])

print(f'test.shape{test.shape}')
test.to_csv('test.csv')


def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)


TIME_STEPS = 7

# reshape to [samples, time_steps, n_features]

X_train, y_train = create_dataset(train[[variable_name]], train[variable_name], TIME_STEPS)
X_test, y_test = create_dataset(test[[variable_name]], test[variable_name], TIME_STEPS)

print(f'X_train.shape: {X_train.shape}')

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

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.2,
    shuffle=False,
    callbacks=[es]
)

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()
plt.show()

X_train_pred = model.predict(X_train)

train_mae_loss = np.mean(np.abs(X_train_pred - X_train), axis=1)

sns.distplot(train_mae_loss, bins=50, kde=True)
plt.show()

X_test_pred = model.predict(X_test)
test_mae_loss = np.mean(np.abs(X_test_pred - X_test), axis=1)

THRESHOLD = 0.05

test_score_df = pd.DataFrame(index=test[TIME_STEPS:].index)
test_score_df['loss'] = test_mae_loss
test_score_df['threshold'] = THRESHOLD
test_score_df['anomaly'] = test_score_df.loss > test_score_df.threshold
test_score_df[variable_name] = test[TIME_STEPS:][variable_name]

# plt.plot(test_score_df.index, test_score_df.loss, label='loss')
# plt.plot(test_score_df.index, test_score_df.threshold, label='threshold')
# plt.xticks(rotation=25)
# plt.legend()
# plt.show()

anomalies = test_score_df[test_score_df.anomaly == True]
print(anomalies.head())
# print(type(test[TIME_STEPS:].close))
# print(test[TIME_STEPS:].shape)
# print(test[TIME_STEPS:].close.shape)
anomalies.to_csv('anomalies.csv')

yhat = scaler.inverse_transform(anomalies[variable_name].values.reshape(-1, 1)).reshape(-1)
print(yhat)
plt.plot(
    test[TIME_STEPS:].index,
    scaler.inverse_transform(test[TIME_STEPS:][variable_name].values.reshape(-1, 1)),
    label='close price'
)
# df = pd.DataFrame({'timestep': anomalies.index.to_numpy(), 'animalie': yhat})
# df.s
# sns.scatterplot(
#     anomalies.index,
#     scaler.inverse_transform(anomalies[variable_name].values.reshape(-1, 1)).reshape(-1),
#     color=sns.color_palette()[3],
#     s=52,
#     label='anomaly'
# )
# quit()
plt.xticks(rotation=25)
plt.legend()
plt.show()
