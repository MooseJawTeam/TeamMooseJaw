from django.urls import path
from . import views

urlpatterns = [
    #documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/view/<int:doc_id>/', views.view_document, name='view_document'),
    path('documents/download/<int:doc_id>/', views.download_document, name='download_document'),
    path('documents/sign/<int:doc_id>/', views.sign_document, name='sign_document'),
    path('documents/generate/', views.generate_document, name='generate_document'),
    
    #templates
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/edit/<int:template_id>/', views.edit_template, name='edit_template'),
]
