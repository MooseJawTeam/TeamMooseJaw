import os
import base64
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import DocumentTemplate, GeneratedDocument, Users, AdminSignature
import logging

logger = logging.getLogger(__name__)

def generate_pdf(template_id, data, user, admin_name, admin_position):
    """
    Generate a PDF document from an HTML template.
    
    Args:
        template_id (int): ID of the DocumentTemplate to use
        data (dict): Dictionary of data to replace in the template
        user (Users): User object for the document recipient
        admin_name (str): Name of the admin approving/denying
        admin_position (str): Position of the admin
        
    Returns:
        GeneratedDocument: The created document object
    """
    try:
        # Get the template
        template = DocumentTemplate.objects.get(id=template_id)
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{template.name.replace(' ', '_')}_{timestamp}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
        
        # Ensure the documents directory exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Add document ID and generation date if not provided
        if 'document_id' not in data:
            data['document_id'] = f"DOC-{timestamp}"
        if 'generation_date' not in data:
            data['generation_date'] = datetime.now().strftime("%B %d, %Y")
            
        # Add user information
        data['username'] = user.name
        data['useremail'] = user.email
        
        # Add admin information
        data['adminname'] = admin_name
        data['adminposition'] = admin_position
        
        # Get admin's active signature
        admin = Users.objects.get(name=admin_name)
        admin_signature = AdminSignature.objects.filter(admin=admin, is_active=True).first()
        if admin_signature:
            # Convert signature image to base64
            with open(admin_signature.signature_image.path, 'rb') as img_file:
                signature_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            data['admin_signature'] = f"data:image/png;base64,{signature_base64}"
        
        # Determine which template to use based on the decision
        template_name = "approved.html" if data.get('decision') == "Pass" else "denied.html"
        
        # Render the HTML template
        html_string = render_to_string(
            f'pdf_templates/{template_name}',
            data
        )
        
        # Generate PDF
        HTML(string=html_string).write_pdf(pdf_path)
        
        # Create a record of the generated document
        document = GeneratedDocument.objects.create(
            template=template,
            created_by=user,
            file_path=os.path.join('documents', filename),
            context_data=data,
            title=f"{template.name} - {timestamp}"
        )
        
        return document
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise Exception(f"Error generating document: {str(e)}")
