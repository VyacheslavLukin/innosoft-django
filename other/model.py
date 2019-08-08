import pickle

import numpy as np
import json
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def extract_data(sample_data: dict):
    records = []
    features = list()
    for key, data in sample_data.items():
        for value in data.keys():
            features.append(value)
        break

    for timestamp, data in sample_data.items():
        record = {}
        for field in features:
            record[field] = data[field]
        records.append(record)
    return records, features


def diff(list1: list, list2: list) -> list:
    return [item for item in list1 if item not in set(list2)]


with open("Train_JSON.json") as json_file:
    data = json.load(json_file)

records, columns = extract_data(data)
rcols = ['snow_intensity']
# rcols = ['air_temperature']
predictors = diff(columns, rcols)

print(columns)
print(rcols)
print(predictors)

df = pd.DataFrame(records, columns=columns)

X = df[predictors]
y = df[rcols]

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.4)  # train-test split, ratio can be custom
reg = LinearRegression().fit(x_train, y_train)  # training the model

pickle.dump(reg, open("test_model.pickle", 'wb'))

y_pred = reg.predict(x_test)

print(y_pred)
