from django.urls import path

from ums import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name='dashboard'),
    path("admin", views.admin, name='admin'),
]