import msal
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from msal import ConfidentialClientApplication
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
import requests
from .models import (
    Users,
    DocumentTemplate,
    GeneratedDocument,
    DocumentSignature,
    DocumentApproval,
    RCEForm,
    SpecialCircumstanceForm,
    AdminSignature,
)
from .decorators import role_required
from django.contrib import messages
import base64
import os
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
import uuid
from datetime import datetime, timezone
from .pdf_utils import generate_pdf
from django.template.loader import render_to_string




def index(request):
    # Check if user is logged in
    if "user_id" in request.session:
        user_role = request.session.get("user_role", "").lower()
        if user_role == "admin":
            return redirect("admin_dashboard")
        else:
            return redirect("user")
    return render(request, 'ums/welcome.html')

def user(request):
    if "user_id" not in request.session:
        return redirect("ums-login")
    
    user_id = request.session.get("user_id")
    user_data = {
        "name": request.session.get("user_name", "Unknown"),
        "email": request.session.get("user_email", "No Email"),
        "id": user_id,
        "role": request.session.get("user_role", "Basicuser"),
        "status": request.session.get("user_status", "Active")
    }

    # Get pending RCE forms for the user
    pending_rce_forms = RCEForm.objects.filter(
        user_id=user_id,
        status='pending'
    ).order_by('-submitted_at')

    # Get pending Special Circumstance forms for the user
    pending_special_forms = SpecialCircumstanceForm.objects.filter(
        user_id=user_id,
        status='pending'
    ).order_by('-submitted_at')

    context = {
        "user": user_data,
        "pending_rce_forms": pending_rce_forms,
        "pending_special_forms": pending_special_forms
    }

    return render(request, "ums/user.html", context)

@role_required(["Admin"])
def admin_dashboard(request):
    # Check if user is authenticated and active
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the admin dashboard.")
        return redirect("ums-login")
    
    # Get the current user
    current_user = Users.objects.filter(id=request.session["user_id"]).first()
    if not current_user or current_user.status != "Active":
        messages.error(request, "Your account is inactive. Please contact support.")
        return redirect("ums-login")
    
    # Double check the role (case-insensitive)
    if current_user.role.lower() != "admin":
        messages.error(request, "You do not have permission to access the admin dashboard.")
        return redirect("user")
    
    # Get all users except the current admin
    users = Users.objects.exclude(id=request.session["user_id"]).order_by("name")
    
    # Get pending RCE forms
    pending_rce_forms = RCEForm.objects.filter(status='pending').select_related('user').order_by('-submitted_at')
    
    # Get pending Special Circumstance forms
    pending_special_forms = SpecialCircumstanceForm.objects.filter(status='pending').select_related('user').order_by('-submitted_at')
    
    # Prepare admin user data
    admin_user = {
        "name": current_user.name,
        "email": current_user.email,
        "id": current_user.id,
        "role": current_user.role,
        "status": current_user.status
    }
    
    # Handle POST requests for user management
    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        
        try:
            user = Users.objects.get(id=user_id)
            
            if action == "update":
                user.name = request.POST.get("name")
                user.email = request.POST.get("email")
                user.role = request.POST.get("role")
                user.save()
                messages.success(request, f"User {user.name} updated successfully.")
                
            elif action == "delete":
                user_name = user.name
                user.delete()
                messages.success(request, f"User {user_name} deleted successfully.")
                
            elif action == "deactivate":
                user.status = "Inactive"
                user.save()
                messages.success(request, f"User {user.name} deactivated successfully.")

            elif action == "activate":
                user.status = "Active"
                user.save()
                messages.success(request, f"User {user.name} activated successfully.")
                
        except Users.DoesNotExist:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
        return redirect("admin_dashboard")
    
    context = {
        "users": users,
        "admin_user": admin_user,
        "pending_rce_forms": pending_rce_forms,
        "pending_special_forms": pending_special_forms
    }
    
    return render(request, "ums/admin.html", context)

def microsoft_login(request):
    msal_app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH["CLIENT_ID"],
        authority=settings.MICROSOFT_AUTH["AUTHORITY"],
        client_credential=settings.MICROSOFT_AUTH["CLIENT_SECRET"],
    )

    # Generate Microsoft authentication URL
    login_url = msal_app.get_authorization_request_url(
        settings.MICROSOFT_AUTH["SCOPE"],
        redirect_uri=settings.MICROSOFT_AUTH["REDIRECT_URI"]
    )

    return redirect(login_url)

def callback(request):
    #retrieve authorization code provided by microsoft
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Invalid authentication request.")
        return redirect("ums-login")

    msal_app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH["CLIENT_ID"],
        authority=settings.MICROSOFT_AUTH["AUTHORITY"],
        client_credential=settings.MICROSOFT_AUTH["CLIENT_SECRET"],
    )

    try:
        # Exchange authorization code for an access token
        token_response = msal_app.acquire_token_by_authorization_code(
            code, settings.MICROSOFT_AUTH["SCOPE"], redirect_uri=settings.MICROSOFT_AUTH["REDIRECT_URI"]
        )

        if "access_token" not in token_response:
            messages.error(request, "Authentication failed. Please try again.")
            return redirect("ums-login")

        # Fetch user details from Microsoft Graph API
        headers = {"Authorization": f'Bearer {token_response["access_token"]}'}
        user_data = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()

        user_id = user_data.get("id", None)
        user_email = user_data.get("mail", None) or user_data.get("userPrincipalName", None)

        if not user_id or not user_email:
            messages.error(request, "Your Microsoft account is missing an email. Contact support.")
            return redirect("ums-login")

        # Find or create a user in the database
        user, created = Users.objects.get_or_create(
            id=user_id,
            defaults={
                "name": user_data.get("displayName", ""),
                "email": user_email,
                "status": "Active",
            }
        )

        # 🔹 If the user is deactivated, show the error page
        if user.status == "Inactive":
            return render(request, "ums/error.html")

        # Assign default role only for newly created users
        if created:
            user.role = "Basicuser"
        user.save()

        # Store user session
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_email"] = user.email
        request.session["user_role"] = user.role
        request.session["is_authenticated"] = True
        
        # Set session expiry to 24 hours
        request.session.set_expiry(86400)
        
        # Save the session explicitly
        request.session.save()

        # Redirect based on role (case-insensitive comparison)
        if user.role.lower() == "admin":
            return redirect("admin_dashboard")
        return redirect("user")

    except Exception as e:
        messages.error(request, f"Error in authentication: {str(e)}")
        return redirect("ums-login")

def logout(request):
    request.session.flush() # clear session
    return redirect("/")



def submit_rce_form(request):
    if request.method == 'POST':
        RCEForm.objects.create(
            user_id=request.session['user_id'],
            exam_date=request.POST['exam_date'],
            semester=request.POST['semester'],
            comments=request.POST.get('comments', ''),
            status='pending'  # Set initial status as pending
        )
        messages.success(request, "RCE request submitted successfully! It will be reviewed by an administrator.")
        return redirect('user')
    
    # Get all basic users for the student dropdown
    users = Users.objects.filter(role='Basic')
    return render(request, 'forms/rce_form.html', {'users': users})

def submit_special_form(request):
    if request.method == 'POST':
        SpecialCircumstanceForm.objects.create(
            user_id=request.session['user_id'],
            degree=request.POST['degree'],
            graduation_date=request.POST['graduation_date'],
            reason=request.POST['reason'],
            special_request_type=request.POST['special_request_type']
        )
        messages.success(request, "Special Circumstance form submitted successfully!")
        return redirect('user')
    return render(request, 'forms/special_form.html')

def generate_decision_document(form, decision, admin_user):
    """
    Generate a decision document for a form.
    
    Args:
        form: The form object (RCEForm or SpecialCircumstanceForm)
        decision: The decision (Pass/Fail)
        admin_user: The admin user making the decision
        
    Returns:
        GeneratedDocument object
    """
    # Get the appropriate template based on the decision
    template_name = "approved.html" if decision == "Pass" else "denied.html"
    
    # Prepare context data for template
    context = {
        'document_title': f"{form.__class__.__name__} Decision",
        'document_id': str(uuid.uuid4()),
        'generation_date': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        'username': form.user.name,
        'useremail': form.user.email,
        'custom_text': form.reason if hasattr(form, 'reason') else form.comments,
        'adminname': admin_user.name,
        'adminposition': "Administrator",
        'decision': decision
    }
    
    # Create document template if it doesn't exist
    template, created = DocumentTemplate.objects.get_or_create(
        name=f"{decision} Decision Template",
        defaults={
            'description': f"Template for {decision} decisions",
            'html_content': render_to_string(f'pdf_templates/{template_name}', context)
        }
    )
    
    try:
        # Generate the PDF and get the document
        document = generate_pdf(
            template_id=template.id,
            data=context,
            user=form.user,
            admin_name=admin_user.name,
            admin_position="Administrator"
        )

        # Create DocumentApproval record
        DocumentApproval.objects.create(
            document=document,
            approver=admin_user,
            action="Approved" if decision == "Pass" else "Denied",
            comments=context['custom_text']
        )

        return document
    except Exception as e:
        print(f"Error generating document: {str(e)}")  # Debug print
        raise Exception(f"Error generating document: {str(e)}")

@role_required(['Admin'])
def review_rce_form(request, form_id):
    form = get_object_or_404(RCEForm, id=form_id)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug print
        action = request.POST.get('action')
        decision = request.POST.get('decision')
        
        print(f"Action: {action}, Decision: {decision}")  # Debug print
        
        if not decision:
            messages.error(request, 'Please select a decision (Pass/Fail)')
            return render(request, 'ums/review_rce.html', {'form': form})
        
        try:
            if action == 'approve':
                form.status = 'approved'
                form.decision = 'Pass'  # Explicitly set to Pass when approving
                messages.success(request, 'RCE request approved successfully.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Pass', admin_user)
                
            elif action == 'deny':
                form.status = 'denied'
                form.decision = 'Fail'  # Always set to Fail when denied
                messages.success(request, 'RCE request denied.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Fail', admin_user)
            
            form.save()
            print(f"Form saved with status: {form.status}, decision: {form.decision}")  # Debug print
            return redirect('admin_dashboard')
        except Exception as e:
            print(f"Error processing form: {str(e)}")  # Debug print
            messages.error(request, f'Error processing request: {str(e)}')
            return render(request, 'ums/review_rce.html', {'form': form})
    
    return render(request, 'ums/review_rce.html', {'form': form})

@role_required(['Admin'])
def review_special_form(request, form_id):
    form = get_object_or_404(SpecialCircumstanceForm, id=form_id)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug print
        action = request.POST.get('action')
        decision = request.POST.get('decision')
        
        print(f"Action: {action}, Decision: {decision}")  # Debug print
        
        if not decision:
            messages.error(request, 'Please select a decision (Pass/Fail)')
            return render(request, 'ums/review_special.html', {'form': form})
        
        try:
            if action == 'approve':
                form.status = 'approved'
                form.decision = 'Pass'  # Explicitly set to Pass when approving
                messages.success(request, 'Special circumstance request approved successfully.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Pass', admin_user)
                
            elif action == 'deny':
                form.status = 'denied'
                form.decision = 'Fail'  # Always set to Fail when denied
                messages.success(request, 'Special circumstance request denied.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Fail', admin_user)
            
            form.save()
            print(f"Form saved with status: {form.status}, decision: {form.decision}")  # Debug print
            return redirect('admin_dashboard')
        except Exception as e:
            print(f"Error processing form: {str(e)}")  # Debug print
            messages.error(request, f'Error processing request: {str(e)}')
            return render(request, 'ums/review_special.html', {'form': form})
    
    return render(request, 'ums/review_special.html', {'form': form})

def user_requests(request):
    if "user_id" not in request.session:
        return redirect("ums-login")
    
    user_id = request.session.get("user_id")
    
    # Get all RCE forms for the user
    rce_forms = RCEForm.objects.filter(
        user_id=user_id
    ).order_by('-submitted_at')
    
    # Get all Special Circumstance forms for the user
    special_forms = SpecialCircumstanceForm.objects.filter(
        user_id=user_id
    ).order_by('-submitted_at')
    
    context = {
        "rce_forms": rce_forms,
        "special_forms": special_forms
    }
    
    return render(request, "ums/user_requests.html", context)

@role_required(['Admin'])
def upload_signature(request):
    """View for admins to upload their signature"""
    # Get the admin user
    admin = Users.objects.get(id=request.session['user_id'])
    
    # Get current active signature if any
    admin_signature = AdminSignature.objects.filter(admin=admin, is_active=True).first()
    
    if request.method == 'POST':
        try:
            # Deactivate any existing active signature
            AdminSignature.objects.filter(admin=admin, is_active=True).update(is_active=False)
            
            # Create new signature
            signature = AdminSignature.objects.create(
                admin=admin,
                signature_image=request.FILES['signature_image']
            )
            
            messages.success(request, "Signature uploaded successfully")
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f"Error uploading signature: {str(e)}")
            return redirect('upload_signature')
    
    return render(request, 'ums/upload_signature.html', {'admin_signature': admin_signature})

@login_required
def submit_rce(request):
    if request.method == 'GET':
        # Get all basic users for the student dropdown
        users = Users.objects.filter(role='Basic')
        # Get admin's active signature if exists
        admin = Users.objects.get(id=request.session['user_id'])
        admin_signature = AdminSignature.objects.filter(admin=admin, is_active=True).first()
        
        return render(request, 'ums/submit_rce.html', {
            'users': users,
            'admin_signature': admin_signature
        })
    
    if request.method == 'POST':
        try:
            # Get the student being evaluated
            student_id = request.POST.get('student_id')
            student = Users.objects.get(id=student_id, role='Basic')
            
            # Get the admin user
            admin = Users.objects.get(id=request.session['user_id'])
            
            # Handle signature
            signature_option = request.POST.get('signature_option')
            signature_url = None
            
            if signature_option == 'existing':
                # Use existing signature
                admin_signature = AdminSignature.objects.filter(admin=admin, is_active=True).first()
                if admin_signature:
                    signature_url = admin_signature.signature_image.url
            elif signature_option == 'new' and 'signature_image' in request.FILES:
                # Upload new signature
                signature_file = request.FILES['signature_image']
                # Deactivate any existing active signature
                AdminSignature.objects.filter(admin=admin, is_active=True).update(is_active=False)
                # Create new signature
                new_signature = AdminSignature.objects.create(
                    admin=admin,
                    signature_image=signature_file
                )
                signature_url = new_signature.signature_image.url
            
            # Create RCE form
            rce_form = RCEForm.objects.create(
                user=student,
                exam_date=request.POST.get('exam_date'),
                semester=request.POST.get('semester'),
                comments=request.POST.get('comments'),
                decision=request.POST.get('decision'),
                chair_name=request.POST.get('chair_name'),
                member1=request.POST.get('member1'),
                member2=request.POST.get('member2'),
                methodology=request.POST.get('methodology'),
                analysis=request.POST.get('analysis'),
                literature=request.POST.get('literature'),
                status='Pending'
            )

            # Generate PDF
            template = get_template('pdf_templates/rce_evaluation.html')
            context = {
                'student_name': student.name,
                'student_id': student.id,
                'exam_date': rce_form.exam_date,
                'semester': rce_form.semester,
                'methodology': rce_form.methodology,
                'analysis': rce_form.analysis,
                'literature': rce_form.literature,
                'comments': rce_form.comments,
                'chair_name': rce_form.chair_name,
                'member1': rce_form.member1,
                'member2': rce_form.member2,
                'decision': rce_form.decision,
                'admin_signature': signature_url,
                'adminname': admin.name,
                'adminposition': admin.position
            }
            html = template.render(context)
            
            # Generate PDF
            pdf = generate_pdf(html)
            
            # Save PDF to media directory
            filename = f'rce_evaluation_{student.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            filepath = os.path.join('rce_evaluations', filename)
            
            # Ensure directory exists
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'rce_evaluations'), exist_ok=True)
            
            # Save PDF
            with open(os.path.join(settings.MEDIA_ROOT, filepath), 'wb') as f:
                f.write(pdf)
            
            # Update RCE form with PDF path
            rce_form.pdf_path = filepath
            rce_form.save()
            
            messages.success(request, 'RCE evaluation submitted successfully!')
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error submitting RCE evaluation: {str(e)}')
            return redirect('submit_rce')
    
    return redirect('admin_dashboard')

