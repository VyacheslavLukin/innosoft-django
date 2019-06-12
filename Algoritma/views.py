from django.shortcuts import render, redirect
from django.contrib import auth
import json
import pickle
from sklearn.metrics import mean_absolute_error
import numpy as np

import Algoritma.dbutils as db
import Algoritma.utils as autils

# cred = credentials.Certificate('innosoft-django-firebase-adminsdk-kml31-03d2439b89.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'innosoft-django.appspot.com'
# })
# db = firestore.client()
# bucket = storage.bucket()

FILENAME_SIZE = 13
ID_SIZE = 9
PICKLE_EXTENSION = "pickle"

def signin(request):
    if request.method == 'GET':
        return render(request, "signin_page.html")
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = db.signin(email, password)
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
        data = {
            "name": request.POST.get('name'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "role": request.POST.get('account_type'),
            "image": request.FILES.get("image")
        }

        #try except
        user = db.create_account(data)

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

        file = request.FILES.get('file')
        if not file:
            return redirect("market_project")

        info = {
            "user": uid,
            "title": request.POST.get('title'),
            "description": request.POST.get('description'),
            "percentage": int(request.POST.get('percentage')),
        }

        # prj_id = generate_rand_name(9)

        # description = request.POST.get('description')


        json_blob, train_blob, test_blob = autils.split_json(file, info["percentage"])

        test_json = json.loads(test_blob)

        #make dynamic
        testpic_x, testpic_y = autils.split_xy(test_json,
                                        ['dew_point_temperature', 'underground_temperature', 'underground_temperature'])

        train_path = db.upload_file_string(train_blob, extension="json", content_type="application/json")
        test_path = db.upload_file_string(test_blob, extension="json", content_type="application/json")
        json_path = db.upload_file_string(json_blob, extension="json", content_type="application/json")
        testpic_x_path = db.upload_file_string(testpic_x, extension="pickle", content_type="text/plain")
        testpic_y_path = db.upload_file_string(testpic_y, extension="pickle", content_type="text/plain")

        info["data"] = json_path
        info["train_data"] = train_path
        info["test_data"] = test_path
        info["pickle_x"] = testpic_x_path
        info["pickle_y"] = testpic_y_path

        prj_id = db.create_project(info)

        # firedb.child('projects').child(prj_id).child("info").set(data)
        # firedb.child('users').child(uid).child('projects').push({"prj_id": prj_id})

        return redirect('market_project')

def upload_model(request):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':
        return render(request, "upload_model_page.html", {"userdata": user})
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return redirect('upload_model')

        filename = request.POST.get('filename')

        sav_path = db.upload_file(file, extension="pickle", content_type="text/plain")

        info = {
            "user": uid,
            "name": filename,
            "data": sav_path,
        }

        firemodel = db.create_model(info)

        return redirect('upload_model')


def project_index(request):
    user = get_user(request)
    if request.method == 'GET':
        projects = db.get_projects()

        return render(request, "project_index.html", {"projects": projects, "userdata": user})


def project_page(request, prj_id):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':

        project = db.get_project(prj_id, option="full")

        models = db.get_user_models(uid)

        return render(request, "project_page.html",
                      {"project": project, "models": models, "userdata": user})

    if request.method == 'POST':
        mid = request.POST.get("mid")
        model = db.get_model(mid)

        project = db.get_project(prj_id)

        model_file = db.get_file_string(model["data"][0])
        model = pickle.loads(model_file)

        xpickle_file = db.get_file_string(project["pickle_x"][0])
        X = pickle.loads(xpickle_file)

        ypickle_file = db.get_file_string(project["pickle_y"][0])
        y = pickle.loads(ypickle_file)

        y_pred = model.predict(X)

        # checking. Make dynamic
        m = mean_absolute_error(y, y_pred, multioutput='raw_values')

        check_result = np.average(m)

        check_data = {
            "project": prj_id,
            "user": uid,
            "model": mid,
            "result": check_result
        }

        db.create_check_data(check_data)


        return redirect('project_page', prj_id)


def model_index(request):
    user = get_user(request)
    uid = user["id"]
    if request.method == 'GET':
        models = db.get_user_models(uid)

        return render(request, "model_index.html", {"models": models, "userdata": user})

def error404(request):
    return render(request, '404.html')

def temp(request):
    user = get_user(request)
    return render(request, 'base.html', {"userdata": user})


def get_user(request):
    idtoken = request.session['uid']
    user = db.get_user_info(idtoken)
    return user
