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
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name="signout"),
    path('signup/', views.signup, name="signup"),
    path('projects/market/', views.market_project_index, name="market_project_index"),
    path('projects/my/', views.user_project_index, name="user_project_index"),
    path('projects/market/create/', views.create_market_project, name="create_market_project"),
    path('projects/my/create/', views.create_custom_project, name="create_custom_project"),
    path('projects/market/<prj_id>/', views.market_project_page, name="market_project_page"),
    path('projects/my/<prj_id>/', views.custom_project_page, name="custom_project_page"),
    path('projects/market/<prj_id>/join/', views.join_market_project, name="join_market_project"),
    path('projects/invite_user', views.invite_user, name="invite_user"),
    path('models/', views.model_index, name="model_index"),
    path('models/upload/', views.upload_model, name="upload_model"),
    path('admin/', admin.site.urls)
]
