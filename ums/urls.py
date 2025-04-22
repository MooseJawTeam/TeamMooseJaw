from django.urls import path
from . import views
from . import view_document
from .views import submit_term_withdrawal


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
    path('term-withdrawal/', submit_term_withdrawal, name='submit_term_withdrawal'),

    # 🔹 Form Review Routes
    path("review/rce/<int:form_id>/", views.review_rce_form, name="review_rce"),
    path("review/special/<int:form_id>/", views.review_special_form, name="review_special"),
    path("review/term-withdrawal/<int:form_id>/", views.review_term_withdrawal, name="review_term_withdrawal"),

    # 🔹 User Requests Route
    path("requests/", views.user_requests, name="user_requests"),

    # 🔹 Signature Upload Route
    path('upload-signature/', views.upload_signature, name='upload_signature'),
    
    # 🔹 Organizational Management
    path("organization/", views.organization_list, name="organization_list"),
    path("organization/create/", views.organization_create, name="organization_create"),
    path("organization/<int:org_id>/edit/", views.organization_edit, name="organization_edit"),
    path("organization/<int:org_id>/view/", views.organization_view, name="organization_view"),
    path("organization/hierarchy/", views.organization_hierarchy, name="organization_hierarchy"),

    # 🔹 User Organization Assignment
    path("users/assign/", views.assign_user_to_org, name="assign_user_to_org"),
    path("users/<str:user_id>/organizations/", views.user_organizations, name="user_organizations"),
    path("organization/<int:org_id>/users/", views.organization_users, name="organization_users"),

    # 🔹 Approver Management
    path("approvers/", views.approver_list, name="approver_list"),
    path("approvers/manage/<str:user_id>/<int:org_id>/", views.manage_approver, name="manage_approver"),
]

