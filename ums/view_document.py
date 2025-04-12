from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.conf import settings
from django.db import models
import os
from .models import DocumentTemplate, GeneratedDocument, DocumentSignature, DocumentApproval
from ums.models import Users
from ums.decorators import role_required
import os
import json
import subprocess
import uuid
import base64
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@role_required(["admin", "Basicuser"])
def document_list(request):
    """List all generated documents the user has access to"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view documents")
        return redirect('index')
    
    user = get_object_or_404(Users, id=user_id)
    user_role = request.session.get('user_role')
    
    # Get the tab parameter to determine which documents to show
    tab = request.GET.get('tab', 'all')
    
    # Base queryset for all documents
    documents = GeneratedDocument.objects.all()
    
    # Filter based on the selected tab
    if tab == 'pending':
        # Show documents that need signing or have pending approval
        documents = documents.filter(
            models.Q(signed_by__isnull=True) | 
            models.Q(documentapproval__action='Pending')
        ).distinct()
        if user_role.lower() != 'admin':
            documents = documents.filter(created_by=user)
    else:
        # Show all documents the user has access to
        if user_role.lower() != 'admin':
            documents = documents.filter(
                models.Q(created_by=user) | 
                models.Q(signed_by=user) |
                models.Q(documentapproval__approver=user)
            ).distinct()
    
    # Order by creation date
    documents = documents.select_related('template', 'created_by').order_by('-created_at')
    
    context = {
        'documents': documents,
        'current_tab': tab,
        'user_role': user_role,
        'user': user
    }
    
    return render(request, 'ums/document_list.html', context)


@role_required(['Admin', 'Basicuser'])
def view_document(request, document_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please log in to view documents.')
            return redirect('login')

        user = Users.objects.get(id=user_id)
        document = GeneratedDocument.objects.get(id=document_id)

        # Check if user has permission to view this document
        if user.role == 'Basicuser' and document.created_by != user:
            messages.error(request, 'You do not have permission to view this document.')
            return redirect('document_list')

        # Get document signatures
        signatures = DocumentSignature.objects.filter(document=document)
        has_signed = signatures.filter(user=user).exists()

        # Get document approval status
        approval = DocumentApproval.objects.filter(document=document).first()

        # Get the absolute file path for the document
        file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
        if not os.path.exists(file_path):
            messages.error(request, 'Document file not found.')
            return redirect('document_list')

        context = {
            'document': document,
            'signatures': signatures,
            'has_signed': has_signed,
            'approval': approval,
            'user': user,
            'file_path': document.file_path,
            'MEDIA_URL': settings.MEDIA_URL
        }
        return render(request, 'pdfdocs/view_document.html', context)

    except GeneratedDocument.DoesNotExist:
        messages.error(request, 'Document not found.')
        return redirect('document_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('document_list')


@role_required(['Admin', 'Basicuser'])
def download_document(request, document_id):
    """Download a specific document"""
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please log in to download documents.')
            return redirect('login')

        user = Users.objects.get(id=user_id)
        document = GeneratedDocument.objects.get(id=document_id)

        # Check if user has permission to download this document
        if user.role == 'Basicuser' and document.created_by != user:
            messages.error(request, 'You do not have permission to download this document.')
            return redirect('document_list')

        # Get the absolute file path
        file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
        if not os.path.exists(file_path):
            messages.error(request, 'Document file not found.')
            return redirect('document_list')

        # Read the PDF file
        with open(file_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{document.title}.pdf"'
            return response

    except GeneratedDocument.DoesNotExist:
        messages.error(request, 'Document not found.')
        return redirect('document_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('document_list')


@role_required(["Admin", "admin"])
def template_list(request):
    """List all document templates (admin only)"""
    # Debug session data
    print("Session data:", request.session.items())
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        print("No user_id in session")
        messages.error(request, "Please log in to view templates")
        return redirect('index')
    
    # Get user and check role
    try:
        user = get_object_or_404(Users, id=request.session['user_id'])
        print("User found:", user.name, "Role:", user.role)
        
        # Check if user is admin (case-insensitive)
        if user.role.lower() != 'admin':
            print("User is not admin")
            messages.error(request, "You do not have permission to view templates")
            return redirect('user')
        
        # If user is admin, show templates
        templates = DocumentTemplate.objects.all().order_by('name')
        return render(request, 'pdfdocs/template_list.html', {
            'templates': templates,
            'user': user
        })
        
    except Exception as e:
        print("Error in template_list:", str(e))
        messages.error(request, "An error occurred while accessing templates")
        return redirect('index')


@role_required(["admin", "Basicuser"])
def generate_document(request):
    """Generate a new document from a template"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to generate documents")
        return redirect('index')
    
    user = get_object_or_404(Users, id=user_id)
    templates = DocumentTemplate.objects.all().order_by('name')
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        title = request.POST.get('title')
        data = {}
        
        # Get template fields and their values
        template = get_object_or_404(DocumentTemplate, id=template_id)
        
        # Process form data for context
        for key, value in request.POST.items():
            if key.startswith('field_'):
                field_name = key.replace('field_', '')
                data[field_name] = value
        
        try:
            # Use the generate_pdf function from pdf_utils
            from .pdf_utils import generate_pdf
            document = generate_pdf(
                template_id=template_id,
                data=data,
                user=user,
                admin_name=user.name,
                admin_position="Administrator"
            )
            
            messages.success(request, f"Document '{title}' generated successfully")
            return redirect('view_document', doc_id=document.id)
        except Exception as e:
            messages.error(request, f"Error generating document: {str(e)}")
            return redirect('generate_document')
    
    return render(request, 'pdfdocs/generate_document.html', {
        'templates': templates,
        'user': user
    })


@role_required(["admin", "Basicuser"])
def sign_document(request, doc_id):
    """Sign a document"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to sign documents")
        return redirect('index')
    
    user = get_object_or_404(Users, id=user_id)
    document = get_object_or_404(GeneratedDocument, id=doc_id)
    
    # Check if user has already signed
    if DocumentSignature.objects.filter(document=document, user=user).exists():
        messages.warning(request, "You have already signed this document")
        return redirect('view_document', doc_id=doc_id)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature_data')
        
        if not signature_data:
            messages.error(request, "Signature data is required")
            return redirect('sign_document', doc_id=doc_id)
        
        # Create signature record
        DocumentSignature.objects.create(
            document=document,
            user=user,
            signature_data=signature_data
        )
        
        messages.success(request, "Document signed successfully")
        return redirect('view_document', doc_id=doc_id)
    
    return render(request, 'pdfdocs/sign_document.html', {
        'document': document,
        'user': user
    })


@role_required(["admin"])
def create_template(request):
    """Create a new document template (admin only)"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to create templates")
        return redirect('index')
    
    user = get_object_or_404(Users, id=user_id)
    if user.role.lower() != 'admin':
        messages.error(request, "You do not have permission to create templates")
        return redirect('user')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        html_content = request.POST.get('html_content')
        
        if not name or not html_content:
            messages.error(request, "Name and HTML content are required")
            return redirect('create_template')
        
        # Create template
        template = DocumentTemplate.objects.create(
            name=name,
            description=description,
            html_content=html_content
        )
        
        messages.success(request, f"Template '{name}' created successfully")
        return redirect('template_list')
    
    return render(request, 'pdfdocs/create_template.html')


@role_required(["admin"])
def edit_template(request, template_id):
    """Edit an existing document template (admin only)"""
    # Debug session data
    print("Session data:", request.session.items())
    
    # Check if user is logged in
    if not request.session.get('user_id'):
        print("No user_id in session")
        messages.error(request, "Please log in to edit templates")
        return redirect('index')
    
    # Get user and check role
    try:
        user = get_object_or_404(Users, id=request.session['user_id'])
        print("User found:", user.name, "Role:", user.role)
        
        # Check if user is admin (case-insensitive)
        if user.role.lower() != 'admin':
            print("User is not admin")
            messages.error(request, "You do not have permission to edit templates")
            return redirect('user')
        
        # Get the template
        template = get_object_or_404(DocumentTemplate, id=template_id)
        
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            html_content = request.POST.get('html_content')
            
            if not name or not html_content:
                messages.error(request, "Name and HTML content are required")
                return redirect('edit_template', template_id=template_id)
            
            # Update template
            template.name = name
            template.description = description
            template.html_content = html_content
            template.save()
            
            messages.success(request, f"Template '{name}' updated successfully")
            return redirect('template_list')
        
        return render(request, 'pdfdocs/edit_template.html', {
            'template': template,
            'user': user
        })
        
    except Exception as e:
        print("Error in edit_template:", str(e))
        messages.error(request, "An error occurred while editing the template")
        return redirect('index')


def document_approval_list(request):
    """
    View for displaying documents that need approval.
    Only shows documents that are pending approval and the user has permission to approve.
    """
    if not request.session.get('user_id'):
        messages.error(request, "Please log in to view pending approvals.")
        return redirect('index')
    
    user_id = request.session['user_id']
    user_role = request.session.get('user_role')
    
    # Get documents that need approval
    # For admins, show all documents that haven't been signed
    # For regular users, show only documents they need to approve
    if user_role == 'Admin':
        pending_documents = GeneratedDocument.objects.filter(
            signed_by__isnull=True
        ).select_related('template', 'created_by').order_by('-created_at')
    else:
        pending_documents = GeneratedDocument.objects.filter(
            signed_by__isnull=True,
            created_by_id=user_id
        ).select_related('template', 'created_by').order_by('-created_at')
    
    context = {
        'pending_documents': pending_documents,
        'user_role': user_role
    }
    
    return render(request, 'ums/document_approval_list.html', context)
