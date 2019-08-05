from django.shortcuts import render, redirect
from django.contrib import auth
import json
import pickle
import numpy as np
from requests import HTTPError
from sklearn.metrics import mean_absolute_error

import Algoritma.utils as autils
from Algoritma.services.file_service import FileService
from Algoritma.services.model_service import ModelService
from Algoritma.services.project_service import ProjectService
from Algoritma.services.user_service import UserService

FILENAME_SIZE = 13
ID_SIZE = 9
PICKLE_EXTENSION = "pickle"

file_service = FileService.getInstance()
project_service = ProjectService.getInstance()
user_service = UserService.getInstance()
model_service = ModelService.getInstance()

def base(request):
    return redirect('signin')

def signin(request):
    if request.method == 'GET':
        user = get_user(request)
        if user:
            return redirect('user_project_index')
        return render(request, "signin_page.html")
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = user_service.signin(email, password)
        except:
            message = "Invalid credentials"
            return render(request, "signin_page.html", {"message": message})
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        return redirect('user_project_index')


def signout(request):
    auth.logout(request)
    return redirect('signin')


def signup(request):
    if request.method == 'GET':
        user = get_user(request)
        if user:
            return redirect('user_project_index')
        return render(request, "signup_page.html")
    elif request.method == 'POST':
        data = {
            "name": request.POST.get('name'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "role": request.POST.get('account_type'),
            "image": request.FILES.get("image")
        }

        # try except
        user = user_service.create_account(data)

        return redirect('signin')


def create_market_project(request):
    user = get_user(request)
    if not user:
        return redirect('signin')
    uid = user["id"]
    if request.method == 'GET':
        return render(request, "create_market_project_page.html", {"userdata": user})
    elif request.method == 'POST':

        file = request.FILES.get('file')
        if not file:
            return redirect("market_project")

        info = {
            "user": uid,
            "title": request.POST.get('title'),
            "short_desc": request.POST.get('short_desc'),
            "description": request.POST.get('description'),
            "percentage": int(request.POST.get('percentage')),
            "start_date": request.POST.get('start_date'),
            "end_date": request.POST.get('end_date'),
            "eval_rules": request.POST.get('eval_rules'),
            "rules": request.POST.get('rules'),
            "prizes": request.POST.get('prizes'),
            "req_cols": request.POST.getlist('req_cols'),
            "opt_cols": request.POST.getlist('opt_cols'),
        }

        # prj_id = generate_rand_name(9)

        # description = request.POST.get('description')

        json_blob, train_blob, test_blob = autils.split_json(file, info["percentage"])

        test_json = json.loads(test_blob)

        # add optional cols
        testpic_x, testpic_y = autils.split_xy(test_json, info["req_cols"])
        # ['dew_point_temperature', 'underground_temperature', 'underground_temperature']

        train_path = file_service.upload_file_string(train_blob, extension="json", content_type="text/json")
        test_path = file_service.upload_file_string(test_blob, extension="json", content_type="text/json")
        json_path = file_service.upload_file_string(json_blob, extension="json", content_type="text/json")
        testpic_x_path = file_service.upload_file_string(testpic_x, extension="pickle", content_type="text/plain")
        testpic_y_path = file_service.upload_file_string(testpic_y, extension="pickle", content_type="text/plain")

        info["data"] = json_path
        info["train_data"] = train_path
        info["test_data"] = test_path
        info["pickle_x"] = testpic_x_path
        info["pickle_y"] = testpic_y_path

        prj_id = project_service.create_market_project(info)

        # firedb.child('projects').child(prj_id).child("info").set(data)
        # firedb.child('users').child(uid).child('projects').push({"prj_id": prj_id})

        return redirect('market_project_index')


def create_custom_project(request):
    user = get_user(request)

    if user == None:
        return redirect('signin')

    uid = user["id"]
    if request.method == 'GET':
        return render(request, "create_custom_project_page.html", {"userdata": user})
    elif request.method == 'POST':

        file = request.FILES.get('file')
        if not file:
            return redirect("market_project")

        info = {
            "user": uid,
            "title": request.POST.get('title'),
            "description": request.POST.get('description'),
            "percentage": int(request.POST.get('percentage')),
            "eval_rules": request.POST.get('eval_rules'),
            "req_cols": request.POST.getlist('req_cols'),
            "opt_cols": request.POST.getlist('opt_cols'),
        }

        # prj_id = generate_rand_name(9)

        # description = request.POST.get('description')

        json_blob, train_blob, test_blob = autils.split_json(file, info["percentage"])

        test_json = json.loads(test_blob)

        # make dynamic
        testpic_x, testpic_y = autils.split_xy(test_json, info["req_cols"])

        train_path = file_service.upload_file_string(train_blob, extension="json", content_type="text/json")
        test_path = file_service.upload_file_string(test_blob, extension="json", content_type="text/json")
        json_path = file_service.upload_file_string(json_blob, extension="json", content_type="text/json")
        testpic_x_path = file_service.upload_file_string(testpic_x, extension="pickle", content_type="text/plain")
        testpic_y_path = file_service.upload_file_string(testpic_y, extension="pickle", content_type="text/plain")

        info["data"] = json_path
        info["train_data"] = train_path
        info["test_data"] = test_path
        info["pickle_x"] = testpic_x_path
        info["pickle_y"] = testpic_y_path

        prj_id = project_service.create_custom_project(info)

        # firedb.child('projects').child(prj_id).child("info").set(data)
        # firedb.child('users').child(uid).child('projects').push({"prj_id": prj_id})

        return redirect('user_project_index')


def upload_model_kek(request):
    user = get_user(request)

    if user == None:
        return redirect('signin')

    uid = user["id"]
    if request.method == 'GET':
        return render(request, "upload_model_page.html", {"userdata": user})
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return redirect('upload_model')

        filename = request.POST.get('filename')

        sav_path = file_service.upload_file(file, extension="pickle", content_type="text/plain")

        info = {
            "user": uid,
            "name": filename,
            "data": sav_path,
        }

        firemodel = model_service.create_model(info)

        return redirect('upload_model')


def market_project_index(request):
    user = get_user(request)
    if user == None:
        return redirect('signin')

    if request.method == 'GET':
        projects = project_service.get_market_projects()
        return render(request, "market_project_index.html", {"projects": projects, "userdata": user})


def user_project_index(request):
    user = get_user(request)
    if user == None:
        return redirect('signin')
    uid = user["id"]
    if request.method == 'GET':
        # pass
        projects = user_service.get_user_projects(uid)
        return render(request, "user_project_index.html", {"projects": projects, "userdata": user})


def is_participant(user, project):
    project = project_service.get_project(project['id'], "participants")
    if user["id"] in project["participants"]:
        return True
    return False


def market_project_page(request, prj_id):
    user = get_user(request)
    if user == None:
        return redirect('signin')
    uid = user["id"]
    if request.method == 'GET':
        project = project_service.get_project(prj_id, option="full")
        models = user_service.get_user_models(uid)

        return render(request, "market_project_page.html",
                      {"project": project, "models": models, "userdata": user})

    if request.method == 'POST':
        project = project_service.get_project(prj_id)

        # TODO: check if user is a partisipant
        if not is_participant(user, project):
            return redirect('market_project_page', project["id"])

        mid = request.POST.get("mid")
        model = model_service.get_model(mid)

        check_result = check_model(project, model)

        if check_result:
            check_data = {
                "project": project["id"],
                "prj_type": project["type"],
                "user": uid,
                "model": mid,
                "result": check_result
            }

            project_service.create_check_data(check_data, "market")
        return redirect('market_project_page', prj_id)


def check_model(project, model):
    try:
        model_file = file_service.get_file_string(model["data"][0])
        model = pickle.loads(model_file)
    except TypeError:
        return None

    xpickle_file = file_service.get_file_string(project["pickle_x"][0])
    X = pickle.loads(xpickle_file)

    ypickle_file = file_service.get_file_string(project["pickle_y"][0])
    y = pickle.loads(ypickle_file)

    try:
        y_pred = model.predict(X)
    except ValueError:
        return None


    # checking. Make dynamic
    m = mean_absolute_error(y, y_pred, multioutput='raw_values')

    check_result = np.average(m)
    return check_result


def join_market_project(request, prj_id):
    user = get_user(request)
    if user == None:
        return redirect('signin')

    if request.method == 'POST':
        user = get_user(request)
        if user:
            project = project_service.get_project(prj_id)
            project_service.add_participant(project, user)
        return redirect('market_project_page', prj_id)


def custom_project_page(request, prj_id):
    user = get_user(request)
    if user == None:
        return redirect('signin')
    uid = user["id"]
    if request.method == 'GET':
        project = project_service.get_project(prj_id, option="full")

        models = user_service.get_user_models(uid)

        return render(request, "custom_project_page.html",
                      {"project": project, "models": models, "userdata": user})

    if request.method == 'POST':
        project = project_service.get_project(prj_id)

        mid = request.POST.get("mid")
        model = model_service.get_model(mid)

        check_result = check_model(project, model)
        if check_result:
            check_data = {
                "project": project["id"],
                "prj_type": project["type"],
                "user": uid,
                "model": mid,
                "result": check_result
            }

            project_service.create_check_data(check_data, "custom")
        return redirect('custom_project_page', prj_id)


def model_index(request):
    user = get_user(request)
    if user == None:
        return redirect('signin')
    uid = user["id"]
    if request.method == 'GET':
        models = user_service.get_user_models(uid)
        return render(request, "model_index.html", {"models": models, "userdata": user})


def error404(request):
    return render(request, '404.html')


def invite_user(request):
    user = get_user(request)
    if user == None:
        return redirect('signing')
    uid = user["id"]
    user_email = request.POST.get("email")
    prj_id = request.POST.get("prj_id")
    collab_user = user_service.get_user_by_email(user_email)
    if collab_user:
        project = project_service.get_project(prj_id)
        project_service.add_participant(project, collab_user)
    return redirect('custom_project_page', prj_id)


def get_user(request):
    try:
        if request.session.get("uid"):
            idtoken = request.session['uid']
            user = user_service.get_user_info(idtoken)
            return user
        return None
    except HTTPError as e:
        print(e)
        return None
