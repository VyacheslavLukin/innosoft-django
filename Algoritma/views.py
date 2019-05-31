from django.shortcuts import render, redirect
import pyrebase
from django.contrib import auth
import firebase_admin
from firebase_admin import credentials, firestore, storage
import traceback
from collections import namedtuple
import pandas as pd
import json
from sklearn.model_selection import train_test_split
import pickle
from sklearn.metrics import mean_absolute_error
import numpy as np

from Algoritma.utils import *

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


# cred = credentials.Certificate('innosoft-django-firebase-adminsdk-kml31-03d2439b89.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'innosoft-django.appspot.com'
# })
# db = firestore.client()
# bucket = storage.bucket()

def signin(request):
    if request.method == 'GET':
        return render(request, "signin_page.html")
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = fireauth.sign_in_with_email_and_password(email, password)
        except:
            message = "Invalid credentials"
            return render(request, "signin_page.html", {"message": message})
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        return redirect('project_index')

def signout(request):
    auth.logout(request)
    return redirect('signin')

def signup(request):
    if request.method == 'GET':
        return render(request, "signup_page.html")
    elif request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('account_type')
        # password_conf = request.POST.get("password_conf")
        image = request.FILES.get("image")

        try:
            user = fireauth.create_user_with_email_and_password(email, password)
        except Exception as e:
            message = e
            return render(request, 'signup_page.html', {"message": message})

        uid = user['localId']

        firename = "%s.%s" % (generate_rand_name(13), image.name.split(".")[-1])
        image_path = upload_file(image, firename)

        data = {"name": name, "role": role, "image": image_path}

        firedb.child("users").child(uid).child("details").set(data)
        return redirect('signin')


# def org_dataset(request):
#     if request.method == 'GET':
#         return render(request, 'org_dataset_page.html')
#     elif request.method == 'POST':
#         idtoken = request.session['uid']
#         account = fireauth.get_account_info(idtoken)
#         account = account['users'][0]['localId']
#
#         rid = generate_rand_name(9)
#
#         file = request.FILES.get('file')
#
#         filename = request.POST.get('filename')
#
#         perc = request.POST.get('percentage')
#         perc = int(perc)
#
#         json_blob, train_blob, test_blob = split_json(file, perc)
#
#         firename = "%s.%s" % (generate_rand_name(13), file.name.split(".")[-1])
#
#         train_path = upload_file_string(train_blob, firename, "train")
#         test_path = upload_file_string(test_blob, firename, "test")
#         json_path = upload_file_string(json_blob, firename)
#
#         test_json = json.loads(test_blob)
#
#         testpic_x, testpic_y = split_xy(test_json, ["air_temperature", "cloudiness"])
#
#         picklename = "%s.sav" % (generate_rand_name(13))
#
#         testpic_x_path = upload_file_string(testpic_x, picklename, "pickle_x")
#         testpic_y_path = upload_file_string(testpic_y, picklename, "pickle_y")
#
#         data = {
#             "filename": filename,
#             "percentage": perc,
#             "data": json_path,
#             "train_data": train_path,
#             "test_data": test_path,
#             "pickle_x": testpic_x_path,
#             "pickle_y": testpic_y_path
#         }
#
#         firedb.child('users').child(account).child('datasets').child(rid).set(data)
#
#         return redirect('check_report')


def market_project(request):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':
        return render(request, "market_project_page.html", {"userdata": user})
    elif request.method == 'POST':

        prj_id = generate_rand_name(9)

        title = request.POST.get('title')
        description = request.POST.get('description')

        file = request.FILES.get('file')

        perc = request.POST.get('percentage')
        perc = int(perc)

        json_blob, train_blob, test_blob = split_json(file, perc)

        basename = generate_rand_name(13)

        firename = "%s.%s" % (basename, file.name.split(".")[-1])

        train_path = upload_file_string(train_blob, firename, "train")
        test_path = upload_file_string(test_blob, firename, "test")
        json_path = upload_file_string(json_blob, firename)

        test_json = json.loads(test_blob)

        testpic_x, testpic_y = split_xy(test_json,
                                        ['dew_point_temperature', 'underground_temperature', 'underground_temperature'])

        picklename = "%s.sav" % (basename)

        testpic_x_path = upload_file_string(testpic_x, picklename, "pickle_x")
        testpic_y_path = upload_file_string(testpic_y, picklename, "pickle_y")

        data = {
            "user": uid,
            "title": title,
            "description": description,
            "percentage": perc,
            "data": json_path,
            "train_data": train_path,
            "test_data": test_path,
            "pickle_x": testpic_x_path,
            "pickle_y": testpic_y_path,
            "firename": firename.split(".")[0]
        }

        firedb.child('projects').child(prj_id).child("info").set(data)
        firedb.child('users').child(uid).child('projects').push({"prj_id": prj_id})

        return redirect('market_project')

def upload_model(request):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':
        return render(request, "upload_model_page.html", {"userdata": user})
    if request.method == 'POST':
        mid = generate_rand_name(9)

        file = request.FILES.get('file')

        filename = request.POST.get('filename')

        firename = "%s.%s" % (generate_rand_name(13), file.name.split(".")[-1])

        sav_path = upload_file(file, firename)

        data = {
            "user": uid,
            "name": filename,
            "data": sav_path,
            "firename": firename.split(".")[0]
        }

        firedb.child('models').child(mid).set(data)
        firedb.child('users').child(uid).child('models').push({"mid": mid, "name": filename, "userdata": user})

        return redirect('upload_model')


def project_index(request):
    user = get_user(request)
    if request.method == 'GET':
        prj_keys = firedb.child('projects').shallow().get().val()

        projects = []
        if prj_keys:
            for key in prj_keys:
                prj = firedb.child('projects').child(key).child("info").get().val()
                prj["id"] = key
                projects.append(dict(prj))

        return render(request, "project_index.html", {"projects": projects, "userdata": user})


def project_page(request, prj_id):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':
        project = firedb.child('projects').child(prj_id).child("info").get().val()
        project["id"] = prj_id
        project = dict(project)

        model_keys = firedb.child('users').child(uid).child("models").shallow().get().val()

        models = []
        if model_keys:
            for key in model_keys:
                model = firedb.child('users').child(uid).child("models").child(key).get().val()
                models.append(dict(model))

        res_keys = firedb.child('projects').child(prj_id).child("results").shallow().get().val()

        results = []
        if res_keys:
            for key in res_keys:
                res_info = firedb.child("projects").child(prj_id).child("results").child(key).get().val()
                # model = firedb.child("models").child(res_info["model"]).get().val()
                # res_info["model"] = dict(model)
                user = firedb.child("users").child(uid)
                user = user.child("details").get().val()
                res_info["user"] = dict(user)
                results.append(res_info)

        return render(request, "project_page.html",
                      {"project": project, "models": models, "results": results, "userdata": user})

    if request.method == 'POST':
        mid = request.POST.get("mid")
        model = firedb.child('models').child(mid).get().val()
        project = firedb.child('projects').child(prj_id).child("info").get().val()

        model_path = "%s.sav" % (model["firename"])
        xpickle_path = "%s_pickle_x.sav" % (project["firename"])
        ypickle_path = "%s_pickle_y.sav" % (project["firename"])

        model_blob = bucket.get_blob(model_path)
        model_pickle = model_blob.download_as_string()
        model = pickle.loads(model_pickle)

        xpickle_blob = bucket.get_blob(xpickle_path)
        xpickle = xpickle_blob.download_as_string()
        X = pickle.loads(xpickle)

        ypicle_blob = bucket.get_blob(ypickle_path)
        ypickle = ypicle_blob.download_as_string()

        y = pickle.loads(ypickle)
        y_pred = model.predict(X)

        # checking
        m = mean_absolute_error(y, y_pred, multioutput='raw_values')

        check_result = np.average(m)

        check_data = {
            "user": uid,
            "model": mid,
            "result": check_result
        }

        firedb.child("projects").child(prj_id).child("results").push(check_data)

        return redirect('project_page', prj_id)


def model_index(request):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':

        model_keys = firedb.child('users').child(uid).child("models").shallow().get().val()

        models = []
        for key in model_keys:
            model = firedb.child('users').child(uid).child("models").child(key).get().val()
            model["id"] = key
            models.append(dict(model))

        return render(request, "model_index.html", {"models": models, "userdata": user})


def error404(request):
    return render(request, '404.html')


def temp(request):
    user = get_user(request)

    return render(request, 'base.html', {"userdata": user})


def get_user(request):
    idtoken = request.session['uid']
    account = fireauth.get_account_info(idtoken)
    account = account['users'][0]['localId']

    user = firedb.child("users").child(account).child("details").get().val()
    user["id"] = account
    user = dict(user)

    return user
