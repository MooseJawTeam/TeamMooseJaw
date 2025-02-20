from django.urls import path

from ums import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user", views.user, name='user'),
    path("admin", views.admin, name='admin'),

]