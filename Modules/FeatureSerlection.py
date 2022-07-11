import numpy as np
import pandas as pd
import seaborn as sns
from featurewiz import featurewiz
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

np.random.seed(1234)


def auto_select_features(input_data, out_targe):
    features, train = featurewiz(input_data, out_targe, corr_limit=0.7, verbose=2, sep=",",
                                 header=0, test_data="", feature_engg="", category_encoders="")
    return features, train


def feature_selection():
    data = pd.read_csv('data/FOE.csv')

    data.Date = pd.to_datetime(data.Date)
    data.set_index("Date", inplace=True)
    X = data.drop(['Close'], axis=1)

    y = data.Close.values

    X_scaled = StandardScaler().fit_transform(X)
    scaled_features = pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
    X_train, X_valid, y_train, y_valid = train_test_split(scaled_features, y, test_size=0.2, random_state=0,
                                                          shuffle=False)

    target = 'Close'
    # Here be Dragons
    reducedFeatures, new_features = auto_select_features(data, target)
    X_new = new_features.drop(['Close'], axis=1)
    y = new_features.Close.values
    X_scaled = StandardScaler().fit_transform(X_new)
    scaled_features = pd.DataFrame(X_scaled, index=X_new.index, columns=X_new.columns)

    X_train, X_valid, y_train, y_valid = train_test_split(scaled_features, y, test_size=0.2, random_state=0,
                                                          shuffle=False)

    classifier = RandomForestRegressor()

    classifier.fit(X_train, y_train)
    # make prediction
    prediction = classifier.predict(X_valid)

    df = pd.DataFrame({'truth': y_valid, 'prediction': prediction}, index=X_valid.index)
    print(df.iloc[-10:, :])
    a4_dims = (11.7, 12)
    fig, ax = plt.subplots(figsize=a4_dims)
    g = sns.lineplot(ax=ax, data=df.iloc[-10:, :])
    plt.xticks(rotation=45)
    plt.show()
