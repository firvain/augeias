import tensorflow as tf
from tensorflow.keras.callbacks import CSVLogger, EarlyStopping

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import time
import gc
import sys
import pendulum

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False
# Data Loader Parameters
BATCH_SIZE = 256
BUFFER_SIZE = 10000
TRAIN_SPLIT = 300000

# LSTM Parameters
EVALUATION_INTERVAL = 200
EPOCHS = 4
PATIENCE = 5

# Reproducibility
SEED = 13
tf.random.set_seed(SEED)


def show_plot(plot_data, delta, title):
    labels = ['History', 'True Future', 'Model Prediction']
    marker = ['.-', 'rx', 'go']
    time_steps = create_time_steps(plot_data[0].shape[0])
    if delta:
        future = delta
    else:
        future = 0

    plt.title(title)
    for i, x in enumerate(plot_data):
        if i:
            plt.plot(future, plot_data[i], marker[i], markersize=10,
                     label=labels[i])
        else:
            plt.plot(time_steps, plot_data[i].flatten(), marker[i], label=labels[i])
        plt.legend()
        plt.xlim([time_steps[0], (future + 5) * 2])
        plt.xlabel('Time-Step')

    return plt


def multivariate_data(dataset, target, start_index, end_index, history_size,
                      target_size, step, single_step=False):
    data = []
    labels = []

    start_index = start_index + history_size
    if end_index is None:
        end_index = len(dataset) - target_size

    for i in range(start_index, end_index):
        indices = range(i - history_size, i, step)
        data.append(dataset[indices])

        if single_step:
            labels.append(target[i + target_size])
        else:
            labels.append(target[i:i + target_size])

    return np.array(data), np.array(labels)


def create_time_steps(length):
    return list(range(-length, 0))


def multi_step_plot(history, true_future, prediction):
    STEP = 6
    plt.figure(figsize=(18, 6))
    num_in = create_time_steps(len(history))
    num_out = len(true_future)

    plt.plot(num_in, np.array(history[:, 1]), label='History')
    plt.plot(np.arange(num_out) / STEP, np.array(true_future), 'bo',
             label='True Future')
    if prediction.any():
        plt.plot(np.arange(num_out) / STEP, np.array(prediction), 'ro',
                 label='Predicted Future')
    plt.legend(loc='upper left')
    plt.show()


def plot_train_history(history, title):
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(len(loss))

    plt.figure()

    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title(title)
    plt.legend()

    plt.show()


def weather():
    zip_path = tf.keras.utils.get_file(
        origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip',
        fname='jena_climate_2009_2016.csv.zip',
        extract=True)
    csv_path, _ = os.path.splitext(zip_path)

    df = pd.read_csv(csv_path)
    print("DataFrame Shape: {} rows, {} columns".format(*df.shape))
    print(df.head())

    features_considered = ['p (mbar)', 'T (degC)', 'rho (g/m**3)']
    features = df[features_considered]
    features.index = df['Date Time']
    features.head()
    features.plot(subplots=True)

    dataset = features.values
    data_mean = dataset[:TRAIN_SPLIT].mean(axis=0)
    data_std = dataset[:TRAIN_SPLIT].std(axis=0)
    dataset = (dataset - data_mean) / data_std

    print(pd.DataFrame(dataset, columns=features.columns, index=features.index).head())
    past_history = 720
    future_target = 72
    STEP = 6

    x_train_multi, y_train_multi = multivariate_data(dataset, dataset[:, 1], 0,
                                                     TRAIN_SPLIT, past_history,
                                                     future_target, STEP)
    x_val_multi, y_val_multi = multivariate_data(dataset, dataset[:, 1],
                                                 TRAIN_SPLIT, None, past_history,
                                                 future_target, STEP)
    print(x_train_multi.shape,
          y_train_multi.shape,
          'Single window of past history : {}'.format(x_train_multi[0].shape),
          'Target temperature to predict : {}'.format(y_train_multi[0].shape),
          sep='\n')
    quit()
    train_data_multi = tf.data.Dataset.from_tensor_slices((x_train_multi, y_train_multi))
    train_data_multi = train_data_multi.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

    val_data_multi = tf.data.Dataset.from_tensor_slices((x_val_multi, y_val_multi))
    val_data_multi = val_data_multi.batch(BATCH_SIZE).repeat()

    for x, y in train_data_multi.take(1):
        multi_step_plot(x[0], y[0], np.array([0]))

    multi_step_model = tf.keras.models.Sequential()
    multi_step_model.add(tf.keras.layers.LSTM(32,
                                              return_sequences=True,
                                              input_shape=x_train_multi.shape[-2:]))
    multi_step_model.add(tf.keras.layers.LSTM(16, activation='relu'))
    multi_step_model.add(tf.keras.layers.Dense(72))

    multi_step_model.compile(optimizer=tf.keras.optimizers.RMSprop(clipvalue=1.0), loss='mae')
    print(multi_step_model.summary())

    for x, y in val_data_multi.take(1):
        print(multi_step_model.predict(x).shape)

    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    multi_step_history = multi_step_model.fit(train_data_multi,
                                              epochs=EPOCHS,
                                              steps_per_epoch=EVALUATION_INTERVAL,
                                              validation_data=val_data_multi,
                                              validation_steps=EVALUATION_INTERVAL,
                                              callbacks=[early_stopping])
    plot_train_history(multi_step_history, 'Multi-Step Training and validation loss')
    for x, y in val_data_multi.take(3):
        print(x)
        print(y)
        multi_step_plot(x[0], y[0], multi_step_model.predict(x)[0])
