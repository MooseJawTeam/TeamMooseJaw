from django.urls import path
<<<<<<< HEAD
from . import views

urlpatterns = [
    path("", views.index, name="welcome"),
    path("user/", views.user, name="user"),
    path("login/", views.microsoft_login, name="login"),
    path("auth/callback/", views.callback, name="auth_callback"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("logout/", views.logout, name="logout"),
]
=======

from ums import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user", views.user, name='user'),
    path("admin", views.admin, name='admin'),

]
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891
