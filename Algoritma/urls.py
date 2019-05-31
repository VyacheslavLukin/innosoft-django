"""Algoritma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('reports/create', views.create_report, name="create_report"),
    path('reports/check', views.check_report, name="check_report"),
    path('orgdataset', views.org_dataset, name="org_dataset"),
    path('projects', views.project_index, name="project_index"),
    path('projects/market', views.market_project, name="market_project"),
    path('projects/<prj_id>', views.project_page, name="project_page"),
    path('models/', views.model_index, name="model_index"),
    path('models/upload', views.upload_model, name="upload_model"),
    path('admin/', admin.site.urls),
    path('temp/', views.temp, name='temp')
    # path(r'/')
]
