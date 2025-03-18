from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="welcome"),
    path("user/", views.user, name="user"),
    path("login/", views.microsoft_login, name="ums-login"),
    path("auth/callback/", views.callback, name="auth_callback"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("logout/", views.logout, name="ums-logout"),
]
