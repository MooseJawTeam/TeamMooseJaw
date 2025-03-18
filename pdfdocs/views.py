from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.conf import settings
from django.db import models
import os
from .models import DocumentTemplate, GeneratedDocument, DocumentSignature
from ums.models import Users
from ums.decorators import role_required
import os
import json
import subprocess
import uuid
import base64
from datetime import datetime


@role_required(["admin", "Basicuser"])
def document_list(request):
    """List all generated documents the user has access to"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view documents")
        return redirect('welcome')
    user = get_object_or_404(Users, id=user_id)
    
    # Admins can see all documents
    if user.is_admin():
        documents = GeneratedDocument.objects.all().order_by('-created_at')
    else:
        # Users can see documents they created or signed
        documents = GeneratedDocument.objects.filter(
            models.Q(created_by=user) | models.Q(signed_by=user)
        ).distinct().order_by('-created_at')
    
    return render(request, 'pdfdocs/document_list.html', {
        'documents': documents,
        'user': user
    })


@role_required(["admin", "Basicuser"])
def view_document(request, doc_id):
    """View a specific document"""
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    document = get_object_or_404(GeneratedDocument, id=doc_id)
    
    # Check permissions
    if not user.is_admin() and user != document.created_by and not document.signed_by.filter(id=user.id).exists():
        messages.error(request, "You don't have permission to view this document")
        return redirect('document_list')
    
    signatures = DocumentSignature.objects.filter(document=document).order_by('timestamp')
    
    # Check if the user has already signed
    already_signed = DocumentSignature.objects.filter(document=document, user=user).exists()
    
    return render(request, 'pdfdocs/view_document.html', {
        'document': document,
        'signatures': signatures,
        'user': user,
        'already_signed': already_signed
    })


@role_required(["admin", "Basicuser"])
def download_document(request, doc_id):
    """Download the PDF document"""
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    document = get_object_or_404(GeneratedDocument, id=doc_id)
    
    # Check permissions
    if not user.is_admin() and user != document.created_by and not document.signed_by.filter(id=user.id).exists():
        messages.error(request, "You don't have permission to download this document")
        return redirect('document_list')
    
    file_path = document.get_absolute_file_path()
    if not os.path.exists(file_path):
        messages.error(request, "Document file not found")
        return redirect('document_list')
    
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"{document.title}.pdf")
    return response


@role_required(["admin"])
def template_list(request):
    """List all available document templates (admin only)"""
    templates = DocumentTemplate.objects.all().order_by('name')
    return render(request, 'pdfdocs/template_list.html', {
        'templates': templates
    })


@role_required(["admin"])
def create_template(request):
    """Create a new LaTeX template (admin only)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        latex_content = request.POST.get('latex_content')
        
        if not name or not latex_content:
            messages.error(request, "Name and LaTeX content are required")
            return redirect('template_list')
        
        template = DocumentTemplate.objects.create(
            name=name,
            description=description,
            latex_content=latex_content
        )
        messages.success(request, f"Template '{name}' created successfully")
        return redirect('template_list')
    
    return render(request, 'pdfdocs/create_template.html')


@role_required(["admin"])
def edit_template(request, template_id):
    """Edit an existing LaTeX template (admin only)"""
    template = get_object_or_404(DocumentTemplate, id=template_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        latex_content = request.POST.get('latex_content')
        
        if not name or not latex_content:
            messages.error(request, "Name and LaTeX content are required")
            return redirect('edit_template', template_id=template.id)
        
        template.name = name
        template.description = description
        template.latex_content = latex_content
        template.save()
        
        messages.success(request, f"Template '{name}' updated successfully")
        return redirect('template_list')
    
    return render(request, 'pdfdocs/edit_template.html', {
        'template': template
    })


@role_required(["admin", "Basicuser"])
def generate_document(request):
    """Generate a new PDF document from a template"""
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    
    # Only admins or basic users can generate documents
    if not (user.is_admin() or user.is_basic_user()):
        messages.error(request, "You don't have permission to generate documents")
        return redirect('document_list')
    
    templates = DocumentTemplate.objects.all().order_by('name')
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        title = request.POST.get('title')
        context_data = request.POST.get('context_data', '{}')
        
        if not template_id or not title:
            messages.error(request, "Template and title are required")
            return render(request, 'pdfdocs/generate_document.html', {
                'templates': templates
            })
        
        template = get_object_or_404(DocumentTemplate, id=template_id)
        
        try:
            context_data = json.loads(context_data)
        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON in context data")
            return render(request, 'pdfdocs/generate_document.html', {
                'templates': templates
            })
        
        # Add user and date information to context
        context_data['user_name'] = user.name
        context_data['user_email'] = user.email
        context_data['generation_date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join('pdfs', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, output_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Generate the document
        success = generate_pdf(template.latex_content, context_data, full_path)
        
        if not success:
            messages.error(request, "Failed to generate PDF document")
            return render(request, 'pdfdocs/generate_document.html', {
                'templates': templates
            })
        
        # Save document in database
        document = GeneratedDocument.objects.create(
            title=title,
            template=template,
            created_by=user,
            file_path=output_path,
            context_data=context_data
        )
        
        messages.success(request, f"Document '{title}' generated successfully")
        return redirect('view_document', doc_id=document.id)
    
    return render(request, 'pdfdocs/generate_document.html', {
        'templates': templates
    })


@role_required(["admin", "Basicuser"])
def sign_document(request, doc_id):
    """Sign a document with digital signature"""
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    document = get_object_or_404(GeneratedDocument, id=doc_id)
    
    # Check if user already signed
    if DocumentSignature.objects.filter(document=document, user=user).exists():
        messages.error(request, "You have already signed this document")
        return redirect('view_document', doc_id=document.id)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature_data')
        
        if not signature_data:
            messages.error(request, "Signature is required")
            return redirect('sign_document', doc_id=document.id)
        
        # Create signature record
        signature = DocumentSignature.objects.create(
            document=document,
            user=user,
            signature_data=signature_data
        )
        
        # Apply the signature to the PDF
        apply_signature_to_pdf(document, signature)
        
        messages.success(request, "Document signed successfully")
        return redirect('view_document', doc_id=document.id)
    
    return render(request, 'pdfdocs/sign_document.html', {
        'document': document,
        'user': user
    })


def generate_pdf(latex_content, context_data, output_path):
    """Generate PDF using LaTeX and provided context data"""
    # Create a temporary directory
    temp_dir = f"/tmp/latex_{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create LaTeX file with context data inserted
    latex_with_context = latex_content
    for key, value in context_data.items():
        placeholder = f"{key}_placeholder"
        latex_with_context = latex_with_context.replace(placeholder, str(value))
    
    tex_file = os.path.join(temp_dir, "document.tex")
    with open(tex_file, 'w') as f:
        f.write(latex_with_context)
    
    # Run make to generate PDF
    makefile_content = f"\"""\n\
    # LaTeX PDF generation Makefile\n\
    TEX = {tex_file}\n\
    PDF = {output_path}\n\
    \n\
    all: $(PDF)\n\
    \n\
    $(PDF): $(TEX)\n\
    \tpdflatex -interaction=nonstopmode -output-directory={temp_dir} $(TEX)\n\
    \tmv {temp_dir}/document.pdf $(PDF)\n\
    \n\
    clean:\n\
    \trm -f {temp_dir}/*.aux {temp_dir}/*.log {temp_dir}/*.out\n\
    """
    
    makefile_path = os.path.join(temp_dir, "Makefile")
    with open(makefile_path, 'w') as f:
        f.write(makefile_content)
    
    try:
        subprocess.run(["make", "-C", temp_dir], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        # Clean up auxiliary files
        subprocess.run(["make", "-C", temp_dir, "clean"], capture_output=True)


def apply_signature_to_pdf(document, signature):
    """Apply digital signature to the PDF file"""
    # For this implementation, we'll use a simple approach
    # In a production environment, you would use a library like endesive for proper digital signatures
    
    # Get the PDF file path
    pdf_path = document.get_absolute_file_path()
    
    # Create signature annotation data
    signature_data = {
        "user": signature.user.name,
        "email": signature.user.email,
        "timestamp": signature.timestamp.isoformat(),
        "signature": signature.signature_data
    }
    
    # In a real implementation, you would:
    # 1. Use a proper PDF library to add the signature to the document
    # 2. Generate and embed a digital signature using cryptographic methods
    # 3. Apply the signature to the PDF in a way that ensures document integrity
    
    # For this implementation, we'll just update the signature record to reflect that it's been applied
    signature.is_valid = True
    signature.save()
