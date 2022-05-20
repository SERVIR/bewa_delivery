from django.urls import path, re_path

from directory import views

urlpatterns = [
    re_path(r'^(?P<path>.*)$', views.browse, name='directory_browse'),
]