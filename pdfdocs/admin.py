from django.contrib import admin
from .models import DocumentTemplate, GeneratedDocument, DocumentSignature

admin.site.register(DocumentTemplate)
admin.site.register(GeneratedDocument)
admin.site.register(DocumentSignature)
