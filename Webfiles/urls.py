"""
URL configuration for Webfiles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from storage import views, consumers
from django.contrib.auth import views as auth_views

router = DefaultRouter()
from django.urls import re_path

urlpatterns = [
    path('', views.index, name='index'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('language/<str:lang>/', views.set_language, name='language'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view , name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('upload/', views.upload_file, name='upload_file'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('create_file/', views.create_file, name='create_file'),
    path('get_folder_contents/', views.get_folder_contents, name='get_folder_contents'),
    path('download/<uuid:file_id>/', views.download_file, name='download_file'),
    path('open/<uuid:file_id>/', views.open_file, name='open_file'),
    path('rename_file/<uuid:file_id>/', views.rename_file, name='rename_file'),
    path('rename_folder/<uuid:folder_id>/', views.rename_folder, name='rename_folder'),
    path('toggle_file_access/<uuid:file_id>/', views.toggle_file_access, name='toggle_file_access'),
    path('toggle_folder_access/<uuid:folder_id>/', views.toggle_folder_access, name='toggle_folder_access'),
    path('delete_file/<uuid:file_id>/', views.delete_file, name='delete_file'),
    path('delete_folder/<uuid:folder_id>/', views.delete_folder, name='delete_folder'),
    re_path(r'^(?P<folder_path>.+)/$', views.index, name='folder_path'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]