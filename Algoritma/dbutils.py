import pyrebase
import Algoritma.utils as utils
import firebase_admin
from firebase_admin import credentials, firestore, storage

FILENAME_SIZE = 13
ID_SIZE = 9

config = {
    "apiKey": "AIzaSyCEEBWHipEhE8wjQNXVtmd0CDUUEUq9kGQ",
    "authDomain": "innosoft-django.firebaseapp.com",
    "databaseURL": "https://innosoft-django.firebaseio.com",
    "projectId": "innosoft-django",
    "storageBucket": "innosoft-django.appspot.com",
    "messagingSenderId": "728530690260",
    "appId": "1:728530690260:web:790af9c28f5476e8"
}

firebase = pyrebase.initialize_app(config)
fireauth = firebase.auth()
firedb = firebase.database()

cred = credentials.Certificate('innosoft-django-firebase-adminsdk-kml31-03d2439b89.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'innosoft-django.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()


def upload_file(file, nlength=FILENAME_SIZE, extension=None, content_type=None):
    if not extension:
        extension = file.name.split(".")[-1]
    if not content_type:
        content_type = file.content_type
    blobname = "%s.%s" % (utils.generate_rand_name(nlength), extension)
    blob = bucket.blob(blobname)
    blob.upload_from_file(file, content_type=content_type)
    path = blob.public_url
    return blobname, path


def upload_file_string(file, nlength=FILENAME_SIZE, extension=None, content_type="text/plain"):
    if not extension:
        extension = file.name.split(".")[-1]
    if not content_type:
        content_type = file.content_type
    blobname = "%s.%s" % (utils.generate_rand_name(nlength), extension)
    blob = bucket.blob(blobname)
    blob.upload_from_string(file, content_type=content_type)
    path = blob.public_url
    return blobname, path


# def upload_file(file, filename, suffix=None):
#     blobname = filename
#     if suffix:
#         blobname = "%s_%s.%s" % (filename.split(".")[0], suffix, filename.split(".")[-1])
#     blob = bucket.blob(blobname)
#     blob.upload_from_file(file)
#     path = blob.public_url
#     return path
#
# def upload_file_string(file, filename, suffix=None):
#     blobname = filename
#     if suffix:
#         blobname = "%s_%s.%s" % (filename.split(".")[0], suffix, filename.split(".")[-1])
#     blob = bucket.blob(blobname)
#     blob.upload_from_string(file)
#     path = blob.public_url
#     return path

def signin(email, password):
    user = fireauth.sign_in_with_email_and_password(email, password)
    return user


def create_account(info):
    # check account
    user = fireauth.create_user_with_email_and_password(info["email"], info["password"])
    uid = user["localId"]
    data = {"name": info["name"], "role": info["role"]}
    if info["image"]:
        image_bucket, image_path = upload_file(info["image"], 13)
        data["image"] = image_path
    save_user_info(uid, data)
    return user


def create_account_info(credentials):
    pass


def save_image(image):
    firename = "%s.%s" % (utils.generate_rand_name(13), image.name.split(".")[-1])
    image_path = upload_file(image, firename)
    return image_path


def save_user_info(uid, info: dict):
    data = {"name": info["name"], "role": info["role"], "image": info["image"]}
    firedb.child("users").child(uid).child("details").set(data)


def get_user_info(idtoken):
    account = fireauth.get_account_info(idtoken)
    account = account['users'][0]['localId']

    user = firedb.child("users").child(account).child("details").get().val()
    user["id"] = account
    user = dict(user)

    return user


def get_projects():
    prj_keys = firedb.child('projects').shallow().get().val()

    projects = []
    if prj_keys:
        for key in prj_keys:
            prj = firedb.child('projects').child(key).child("info").get().val()
            prj["id"] = key
            projects.append(dict(prj))

    return projects


def create_project(info: dict):
    user = info["user"]
    prj_id = utils.generate_rand_name(ID_SIZE)
    info.pop("uid")
    firedb.child('projects').child(prj_id).child("info").set(info)
    firedb.child('users').child(user).child('projects').push({"prj_id": prj_id})

    return prj_id

def create_model(info: dict):
    user = info["user"]
    mid = utils.generate_rand_name(ID_SIZE)
    # firedb.child('models').child(mid).set(info)
    firemodel = firedb.child('models').push(info)
    return firemodel
    # firedb.child('users').child(user).child('models').push({"mid": mid, "name": filename, "userdata": user})

# def create_project(info):
