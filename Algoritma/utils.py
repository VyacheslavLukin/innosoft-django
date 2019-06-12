import json
from random import randrange
import pandas as pd
import pickle

# cred = credentials.Certificate('innosoft-django-firebase-adminsdk-kml31-03d2439b89.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'innosoft-django.appspot.com'
# })
# db = firestore.client()
# bucket = storage.bucket()

def generate_rand_name(length) -> str:
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    result = ''
    while len(result) < length:
        result += possible[randrange(len(possible))]
    return result

def split_json(file, percentage):
    json_data = json.load(file)
    json_keys = list(json_data.keys())


    flag = int(len(json_data)/100*percentage)

    train_data = {}
    train_keys = json_keys[:flag]
    for key in train_keys:
        train_data[key] = json_data[key]
    train_blob = json.dumps(train_data)

    test_data = {}
    test_keys = json_keys[flag:]
    for key in test_keys:
        test_data[key] = json_data[key]
    test_blob = json.dumps(test_data)

    orig_blob = json.dumps(json_data)

    return orig_blob, train_blob, test_blob

def upload_file(file, filename, suffix=None):
    blobname = filename
    if suffix:
        blobname = "%s_%s.%s" % (filename.split(".")[0], suffix, filename.split(".")[-1])

    blob = bucket.blob(blobname)
    blob.upload_from_file(file)
    path = blob.public_url
    return path

def upload_file_string(file, filename, suffix=None):
    blobname = filename
    if suffix:
        blobname = "%s_%s.%s" % (filename.split(".")[0], suffix, filename.split(".")[-1])

    blob = bucket.blob(blobname)
    blob.upload_from_string(file)
    path = blob.public_url
    return path

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

def split_xy(json_data, checkers=[]):
    records, features = extract_data(json_data)
    predictors = diff(features, checkers)

    df = pd.DataFrame(records, columns=features)

    X = df[predictors]
    y = df[checkers]

    pickle_x = pickle.dumps(X)
    pickle_y = pickle.dumps(y)

    return pickle_x, pickle_y