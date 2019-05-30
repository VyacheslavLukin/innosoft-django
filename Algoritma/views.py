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

def login(request):
    if request.method == 'GET':
        return render(request, "login_page.html")
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = fireauth.sign_in_with_email_and_password(email, password)
        except:
            message = "Invalid credentials"
            return render(request, "login_page.html", {"message": message})
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        return render(request, "welcome_page.html", {"e": email})

def logout(request):
    auth.logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'GET':
        return render(request, "signup_page.html")
    elif request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = fireauth.create_user_with_email_and_password(email, password)
        except Exception as e:
            message = e
            return render(request, 'signup_page.html', {"message": message})

        uid = user['localId']

        data = {"name": name, "status": "1"}

        firedb.child("users").child(uid).child("details").set(data)
        return redirect('login')

def create_report(request):
    if request.method == 'GET':
        return render(request, "create_report_page.html")
    elif request.method == 'POST':

        rid = generate_rand_name(9)

        work = request.POST.get('work')
        progress = request.POST.get('progress')

        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        data = {
            "work": work,
            "progress": progress
        }

        file = request.FILES.get('file')

        filename = file.name


        firedb.child('users').child(account).child('reports').child(rid).set(data)

        blobname = "%s.%s" % (generate_rand_name(9), filename.split(".")[-1])

        blob = bucket.blob(blobname)
        blob.upload_from_file(file)
        print(blob.public_url)

        return redirect('check_report')

def check_report(request):
    if request.method == 'GET':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']
        print(str(account))

        report_keys = firedb.child('users').child(account).child('reports').shallow().get().val()

        reports = []
        for key in report_keys:
            report = firedb.child('users').child(account).child('reports').child(key).get().val()
            reports.append(dict(report))

        print(reports)

        return render(request, "check_report_page.html", {"reports": reports})

def org_dataset(request):
    if request.method == 'GET':
        return render(request, 'org_dataset_page.html')
    elif request.method == 'POST':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        rid = generate_rand_name(9)

        file = request.FILES.get('file')

        filename = request.POST.get('filename')

        perc = request.POST.get('percentage')
        perc = int(perc)

        json_blob, train_blob, test_blob = split_json(file, perc)

        firename = "%s.%s" % (generate_rand_name(13), file.name.split(".")[-1])

        train_path = upload_file_string(train_blob, firename, "train")
        test_path = upload_file_string(test_blob, firename, "test")
        json_path = upload_file_string(json_blob, firename)

        test_json = json.loads(test_blob)

        testpic_x, testpic_y = split_xy(test_json, ["air_temperature", "cloudiness"])

        picklename = "%s.sav" % (generate_rand_name(13))

        testpic_x_path = upload_file_string(testpic_x, picklename, "pickle_x")
        testpic_y_path = upload_file_string(testpic_y, picklename, "pickle_y")

        data = {
            "filename": filename,
            "percentage": perc,
            "data": json_path,
            "train_data": train_path,
            "test_data": test_path,
            "pickle_x": testpic_x_path,
            "pickle_y": testpic_y_path
        }

        firedb.child('users').child(account).child('datasets').child(rid).set(data)

        return redirect('check_report')

def market_project(request):
    if request.method == 'GET':
        return render(request, "market_project_page.html")
    elif request.method == 'POST':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

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

        testpic_x, testpic_y = split_xy(test_json, ['dew_point_temperature', 'underground_temperature', 'underground_temperature'])

        picklename = "%s.sav" % (basename)

        testpic_x_path = upload_file_string(testpic_x, picklename, "pickle_x")
        testpic_y_path = upload_file_string(testpic_y, picklename, "pickle_y")

        data = {
            "user": account,
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

        firedb.child('projects').child(prj_id).set(data)
        firedb.child('users').child(account).child('projects').push({"prj_id": prj_id})

        return redirect('market_project')

def upload_model(request):
    if request.method == 'GET':
        return render(request, "upload_model_page.html")
    if request.method == 'POST':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        mid = generate_rand_name(9)

        file = request.FILES.get('file')

        filename = request.POST.get('filename')

        firename = "%s.%s" % (generate_rand_name(13), file.name.split(".")[-1])

        sav_path = upload_file(file, firename)

        data = {
            "user": account,
            "name": filename,
            "data": sav_path,
            "firename": firename.split(".")[0]
        }

        firedb.child('models').child(mid).set(data)
        firedb.child('users').child(account).child('models').push({"mid": mid, "name": filename})

        return redirect('upload_model')

def project_index(request):
    if request.method == 'GET':
        prj_keys = firedb.child('projects').shallow().get().val()

        projects = []
        for key in prj_keys:
            prj = firedb.child('projects').child(key).get().val()
            prj["id"] = key
            projects.append(dict(prj))

        return render(request, "project_index.html", {"projects": projects})


def project_page(request, prj_id):
    if request.method == 'GET':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        project = firedb.child('projects').child(prj_id).get().val()
        project["id"] = prj_id
        project = dict(project)

        model_keys = firedb.child('users').child(account).child("models").shallow().get().val()

        models = []
        for key in model_keys:
            model = firedb.child('users').child(account).child("models").child(key).get().val()
            models.append(dict(model))

        return render(request, "project_page.html", {"project": project, "models": models})
    if request.method == 'POST':
        mid = request.POST.get("mid")
        model = firedb.child('models').child(mid).get().val()
        project = firedb.child('projects').child(prj_id).get().val()

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

        return redirect('project_page', prj_id)

def model_index(request):
    if request.method == 'GET':
        idtoken = request.session['uid']
        account = fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        model_keys = firedb.child('users').child(account).child("models").shallow().get().val()

        models = []
        for key in model_keys:
            model = firedb.child('users').child(account).child("models").child(key).get().val()
            model["id"] = key
            models.append(dict(model))

        return render(request, "model_index.html", {"models": models})