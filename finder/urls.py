from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dataset/", views.dataset, name="dataset"),
    path("index/", views.index_page, name="index_page"),
    path("evaluation/", views.evaluation, name="evaluation"),
]
