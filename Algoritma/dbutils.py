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


def get_market_projects():
    prj_keys = firedb.child('projects').child('market').shallow().get().val()

    projects = []
    if prj_keys:
        for key in prj_keys:
            project = get_project(key)
            projects.append(dict(project))

    return projects

MARKET_PROJECT = 'market'
CUSTOM_PROJECT = 'custom'

def create_market_project(info: dict):
    user = info["user"]
    # prj_id = utils.generate_rand_name(ID_SIZE)
    info.pop("user")
    info["owner"] = user
    info["type"] = MARKET_PROJECT
    project = {}
    project["info"] = info
    # firedb.child('projects').child(prj_id).child("info").set(info)
    fireproject = firedb.child('projects').child("market").push(project)
    prj_id = fireproject["name"]
    firedb.child('users').child(user).child('projects').child("own").push({"prj_id": prj_id, "type": MARKET_PROJECT})
    create_project_link(prj_id, MARKET_PROJECT)
    return prj_id

def create_custom_project(info: dict):
    user = info["user"]
    # prj_id = utils.generate_rand_name(ID_SIZE)
    info.pop("user")
    info["owner"] = user
    info["type"] = CUSTOM_PROJECT
    project = {}
    project["info"] = info
    # firedb.child('projects').child(prj_id).child("info").set(info)
    fireproject = firedb.child('projects').child("custom").push(project)
    prj_id = fireproject["name"]
    firedb.child('users').child(user).child('projects').child("own").push({"prj_id": prj_id, "type": CUSTOM_PROJECT})
    create_project_link(prj_id, CUSTOM_PROJECT)
    return prj_id

def create_project_link(prj_id, prj_type):
    firedb.child('projects').child('links').child(prj_id).set({"type": prj_type})

def create_model(info: dict):
    user = info["user"]
    # firedb.child('models').child(mid).set(info)
    firemodel = firedb.child('models').push(info)
    firedb.child('users').child(user).child('models').push({"mid": firemodel["name"], "name": info["name"]})

    return firemodel
    # firedb.child('users').child(user).child('models').push({"mid": mid, "name": filename, "userdata": user})


# def create_project(info):

OPTIONS = ["info", "full", "participants"]

def get_project(prj_id, option=OPTIONS[0]):
    prj_type = firedb.child('projects').child('links').child(prj_id).get().val()["type"]
    project = firedb.child('projects').child(prj_type).child(prj_id).child("info").get().val()
    project["id"] = prj_id
    project = dict(project)
    project["owner"] = get_project_owner_info(project)

    if option == "full":
        project["results"] = get_project_results(project)
        project["participants"] = get_project_participants(project)

    if option == "participants":
        project["participants"] = get_project_participants(project)

    return project

def get_project_owner_info(project):
    user = firedb.child("users").child(project["owner"]).child("details").get().val()
    return dict(user)

def get_project_results(project):
    res_keys = firedb.child('projects').child(project["type"]).child(project["id"]).child("results").shallow().get().val()

    results = []
    if res_keys:
        for key in res_keys:
            res_info = firedb.child("projects").child(project["type"]).child(project["id"]).child("results").child(key).get().val()
            # model = firedb.child("models").child(res_info["model"]).get().val()
            # res_info["model"] = dict(model)
            user = firedb.child("users").child(res_info["user"])
            user = user.child("details").get().val()
            res_info["user"] = dict(user)
            results.append(res_info)

    return results

def get_project_participants(project):
    res_keys = firedb.child('projects').child(project['type']).child(project['id']).child('participants').shallow().get().val()

    participants = {}
    if res_keys:
        for key in res_keys:
            participant_info = firedb.child('projects').child(project['type']).child(project['id']).child('participants').child(key).get().val()

            user_key = participant_info["user"]
            user = firedb.child("users").child(user_key).child("details").get().val()
            participants[user_key] = dict(user)

    return participants


# def get_market_project(prj_id, option=OPTIONS[0]):
#     project = firedb.child('projects').child('market').child(prj_id).child("info").get().val()
#     project["id"] = prj_id
#     project = dict(project)
#
#     if option == "full":
#         res_keys = firedb.child('projects').child('market').child(prj_id).child("results").shallow().get().val()
#
#         results = []
#         if res_keys:
#             for key in res_keys:
#                 res_info = firedb.child("projects").child('market').child(prj_id).child("results").child(key).get().val()
#                 # model = firedb.child("models").child(res_info["model"]).get().val()
#                 # res_info["model"] = dict(model)
#                 user = firedb.child("users").child(res_info["user"])
#                 user = user.child("details").get().val()
#                 res_info["user"] = dict(user)
#                 results.append(res_info)
#
#         project["results"] = results
#     return project

# def get_custom_project(prj_id, option=OPTIONS[0]):
#     project = firedb.child('projects').child('custom').child(prj_id).child("info").get().val()
#     project["id"] = prj_id
#     project = dict(project)
#
#     if option == "full":
#         res_keys = firedb.child('projects').child('custom').child(prj_id).child("results").shallow().get().val()
#
#         results = []
#         if res_keys:
#             for key in res_keys:
#                 res_info = firedb.child("projects").child('custom').child(prj_id).child("results").child(key).get().val()
#                 # model = firedb.child("models").child(res_info["model"]).get().val()
#                 # res_info["model"] = dict(model)
#                 user = firedb.child("users").child(res_info["user"])
#                 user = user.child("details").get().val()
#                 res_info["user"] = dict(user)
#                 results.append(res_info)
#
#         project["results"] = results
#     return project


def get_user_models(user):
    model_keys = firedb.child('users').child(user).child("models").shallow().get().val()

    models = []
    if model_keys:
        for key in model_keys:
            model = firedb.child('users').child(user).child("models").child(key).get().val()
            models.append(dict(model))

    return models


OWN_PROJECTS = "own"
PARTY_PROJECTS = "party"
def get_user_projects(user):
    projects = []
    projects.extend(get_projects_by_user(user, OWN_PROJECTS))
    projects.extend(get_projects_by_user(user, PARTY_PROJECTS))
    return projects

#type: #own or party
def get_projects_by_user(user, type: str):
    project_keys = firedb.child('users').child(user).child('projects').child(type).shallow().get().val()

    projects = []
    if project_keys:
        for key in project_keys:
            prj_info = firedb.child('users').child(user).child('projects').child(type).child(key).get(0).val()
            project = get_project(prj_info["prj_id"])
            # prj = firedb.child('projects').child(prj_info["type"]).child(prj_info["prj_id"]).child("info").get().val()
            # prj["id"] = prj_info["prj_id"]
            projects.append(dict(project))
    return projects

def get_model(mid):
    model = firedb.child('models').child(mid).get().val()
    return model


def get_file_string(name):
    model_blob = bucket.get_blob(name)
    model_pickle = model_blob.download_as_string()
    return model_pickle


def create_check_data(info):
    firedb.child("projects").child(info["prj_type"]).child(info["project"]).child("results").push(info)


def add_participant(project, user):
    party_users = get_party_users(project)
    if not user["id"] in party_users:
        firedb.child("projects").child(project['type']).child(project['id']).child('participants').push({"user": user["id"]})
        firedb.child("users").child(user["id"]).child("projects").child("party").push({"prj_id": project["id"], "type": project["type"]})

def get_party_users(project):
    project = get_project(project["id"], "participants")
    return project["participants"]


