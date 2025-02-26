from django.urls import path
from ums import views

urlpatterns = [
    path("", views.index, name="index"),  # Homepage
#     path("user/",views.user, name="user"),  # User dashboard
#     path("admin-dashboard/", views.admin, name="admin_dashboard"),
    path("login/", views.login, name="login"),
    path("auth/callback/", views.auth_callback, name="auth_callback"),
]
