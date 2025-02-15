from django.urls import path

from ums import views

urlpatterns = [
    path("", views.index, name="index"),
]