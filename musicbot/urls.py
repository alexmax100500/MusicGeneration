from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("getAccords", views.getAccords, name="getAccords"),
    path("getAudio", views.getAudio, name="getAudio"),
    path("uploadFile", views.upload_file, name="upload_file")
]