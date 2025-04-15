from django.urls import path
from . import views
from . import view_document


urlpatterns = [
    # 🔹 Core routes
    path("", views.index, name="index"),
    path("user/", views.user, name="user"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("login/", views.microsoft_login, name="ums-login"),
    path("auth/callback/", views.callback, name="auth_callback"),
    path("logout/", views.logout, name="logout"),

    # 🔹 Document Management
    path("documents/", view_document.document_list, name="document_list"),
    path("documents/<int:document_id>/", view_document.view_document, name="view_document"),
    path("documents/<int:document_id>/download/", view_document.download_document, name="download_document"),
    path("documents/generate/", view_document.generate_document, name="generate_document"),
    path("documents/<int:document_id>/sign/", view_document.sign_document, name="sign_document"),
    path("documents/approvals/", view_document.document_approval_list, name="document_approval_list"),

    # 🔹 Template Management
    path("templates/", view_document.template_list, name="template_list"),
    path("templates/create/", view_document.create_template, name="create_template"),
    path("templates/<int:template_id>/edit/", view_document.edit_template, name="edit_template"),

    # 🔹 Form Submission Routes
    path("submit/rce/", views.submit_rce_form, name="submit_rce"),
    path("submit/special/", views.submit_special_form, name="submit_special"),

    # 🔹 Form Review Routes
    path("review/rce/<int:form_id>/", views.review_rce_form, name="review_rce"),
    path("review/special/<int:form_id>/", views.review_special_form, name="review_special"),

    # 🔹 User Requests Route
    path("requests/", views.user_requests, name="user_requests"),

    # 🔹 Signature Upload Route
    path('upload-signature/', views.upload_signature, name='upload_signature'),
]

