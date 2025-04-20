import msal
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from msal import ConfidentialClientApplication
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
import requests
from django.db.models import Q
from .models import (
    Users,
    DocumentTemplate,
    GeneratedDocument,
    DocumentSignature,
    DocumentApproval,
    RCEForm,
    SpecialCircumstanceForm,
    AdminSignature,
    OrganizationalUnit,
    UserOrganizationAssignment,
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
    
    # Get organizational units
    organizations = OrganizationalUnit.objects.all()
    
    # Get approvers
    approver_assignments = UserOrganizationAssignment.objects.filter(
        Q(is_approver=True) | Q(is_organizational_approver=True)
    ).select_related('user', 'organizational_unit')
    
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
        "pending_special_forms": pending_special_forms,
        "organizations": organizations,
        "approver_assignments": approver_assignments
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

        user_id = user_data.get("id")
        user_email = user_data.get("mail") or user_data.get("userPrincipalName")
        user_name = user_data.get("displayName", "Unknown User")

        if not user_email or not user_id:
            messages.error(request, "Your Microsoft account is missing an email. Contact support.")
            return redirect("ums-login")

        if not(user_email.endswith("@uh.edu") or user_email.endswith("@cougarnet.uh.edu")):
            messages.error(request, "Access restricted to Cougar ID's")
            return redirect("ums-login")

        # Find or create a user in the database
        user, created = Users.objects.get_or_create(
            id=user_id,
            defaults={
                "name": user_data.get("displayName", ""),
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
        # Get organizational unit
        org_unit_id = request.POST.get('organizational_unit')
        org_unit = None
        if org_unit_id:
            org_unit = OrganizationalUnit.objects.get(id=org_unit_id)
            
        RCEForm.objects.create(
            user_id=request.session['user_id'],
            exam_date=request.POST['exam_date'],
            semester=request.POST['semester'],
            comments=request.POST.get('comments', ''),
            organizational_unit=org_unit,
            status='pending'  # Set initial status as pending
        )
        messages.success(request, "RCE request submitted successfully! It will be reviewed by an administrator.")
        return redirect('user')
    
    # Get organizations for form selection
    organizations = OrganizationalUnit.objects.all()
    return render(request, 'forms/rce_form.html', {"organizations": organizations})

def submit_special_form(request):
    if request.method == 'POST':
        # Get organizational unit
        org_unit_id = request.POST.get('organizational_unit')
        org_unit = None
        if org_unit_id:
            org_unit = OrganizationalUnit.objects.get(id=org_unit_id)
            
        SpecialCircumstanceForm.objects.create(
            user_id=request.session['user_id'],
            degree=request.POST['degree'],
            graduation_date=request.POST['graduation_date'],
            reason=request.POST['reason'],
            special_request_type=request.POST['special_request_type'],
            organizational_unit=org_unit
        )
        messages.success(request, "Special Circumstance form submitted successfully!")
        return redirect('user')
        
    # Get organizations for form selection
    organizations = OrganizationalUnit.objects.all()
    return render(request, 'forms/special_form.html', {"organizations": organizations})

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
        name=template_name,  # Use the actual template name instead of constructing one
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
    
    # Check if user has permission to review this form
    user = Users.objects.get(id=request.session['user_id'])
    can_review = True
    
    # If form has organizational unit, check permissions
    if form.organizational_unit:
        # Get all user's organization assignments
        user_assignments = UserOrganizationAssignment.objects.filter(user=user)
        
        # Check if user is an organizational approver in any relevant unit
        is_org_approver = user_assignments.filter(
            is_organizational_approver=True
        ).exists()
        
        # Check if user is a direct approver for the form's unit
        is_unit_approver = user_assignments.filter(
            organizational_unit=form.organizational_unit,
            is_approver=True
        ).exists()
        
        # Check if user is an approver for any ancestor unit
        ancestor_units = []
        if hasattr(form.organizational_unit, 'get_ancestors'):
            ancestor_units = form.organizational_unit.get_ancestors()
            
        is_ancestor_approver = user_assignments.filter(
            organizational_unit__in=ancestor_units,
            is_approver=True
        ).exists()
        
        can_review = is_org_approver or is_unit_approver or is_ancestor_approver or user.role.lower() == 'admin'
    
    if not can_review and user.role.lower() != 'admin':
        messages.error(request, "You don't have permission to review this form")
        return redirect('admin_dashboard')
    
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
                
                # Create document approval with organizational context
                if form.organizational_unit:
                    DocumentApproval.objects.create(
                        document=document,
                        approver=admin_user,
                        action="Approved",
                        comments=f"RCE Form approved by {admin_user.name}",
                        organizational_unit=form.organizational_unit,
                        is_org_level_approval=is_org_approver if 'is_org_approver' in locals() else False
                    )
                
            elif action == 'deny':
                form.status = 'denied'
                form.decision = 'Fail'  # Always set to Fail when denied
                messages.success(request, 'RCE request denied.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Fail', admin_user)
                
                # Create document approval with organizational context
                if form.organizational_unit:
                    DocumentApproval.objects.create(
                        document=document,
                        approver=admin_user,
                        action="Denied",
                        comments=f"RCE Form denied by {admin_user.name}",
                        organizational_unit=form.organizational_unit,
                        is_org_level_approval=is_org_approver if 'is_org_approver' in locals() else False
                    )
            
            form.save()
            print(f"Form saved with status: {form.status}, decision: {form.decision}")  # Debug print
            return redirect('admin_dashboard')
        except Exception as e:
            print(f"Error processing form: {str(e)}")  # Debug print
            messages.error(request, f'Error processing request: {str(e)}')
            return render(request, 'ums/review_rce.html', {'form': form})
    
    # Get organizational context for template
    org_context = None
    if form.organizational_unit:
        ancestors = []
        if hasattr(form.organizational_unit, 'get_ancestors'):
            ancestors = form.organizational_unit.get_ancestors()
            
        org_context = {
            'unit': form.organizational_unit,
            'ancestors': ancestors
        }
    
    return render(request, 'ums/review_rce.html', {
        'form': form,
        'org_context': org_context
    })

@role_required(['Admin'])
def review_special_form(request, form_id):
    form = get_object_or_404(SpecialCircumstanceForm, id=form_id)
    
    # Check if user has permission to review this form
    user = Users.objects.get(id=request.session['user_id'])
    can_review = True
    
    # If form has organizational unit, check permissions
    if form.organizational_unit:
        # Get all user's organization assignments
        user_assignments = UserOrganizationAssignment.objects.filter(user=user)
        
        # Check if user is an organizational approver in any relevant unit
        is_org_approver = user_assignments.filter(
            is_organizational_approver=True
        ).exists()
        
        # Check if user is a direct approver for the form's unit
        is_unit_approver = user_assignments.filter(
            organizational_unit=form.organizational_unit,
            is_approver=True
        ).exists()
        
        # Check if user is an approver for any ancestor unit
        ancestor_units = []
        if hasattr(form.organizational_unit, 'get_ancestors'):
            ancestor_units = form.organizational_unit.get_ancestors()
            
        is_ancestor_approver = user_assignments.filter(
            organizational_unit__in=ancestor_units,
            is_approver=True
        ).exists()
        
        can_review = is_org_approver or is_unit_approver or is_ancestor_approver or user.role.lower() == 'admin'
    
    if not can_review and user.role.lower() != 'admin':
        messages.error(request, "You don't have permission to review this form")
        return redirect('admin_dashboard')
    
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
                
                # Create document approval with organizational context
                if form.organizational_unit:
                    DocumentApproval.objects.create(
                        document=document,
                        approver=admin_user,
                        action="Approved",
                        comments=f"Special Circumstance Form approved by {admin_user.name}",
                        organizational_unit=form.organizational_unit,
                        is_org_level_approval=is_org_approver if 'is_org_approver' in locals() else False
                    )
                
            elif action == 'deny':
                form.status = 'denied'
                form.decision = 'Fail'  # Always set to Fail when denied
                messages.success(request, 'Special circumstance request denied.')
                
                # Generate decision document
                admin_user = Users.objects.get(id=request.session['user_id'])
                document = generate_decision_document(form, 'Fail', admin_user)
                
                # Create document approval with organizational context
                if form.organizational_unit:
                    DocumentApproval.objects.create(
                        document=document,
                        approver=admin_user,
                        action="Denied",
                        comments=f"Special Circumstance Form denied by {admin_user.name}",
                        organizational_unit=form.organizational_unit,
                        is_org_level_approval=is_org_approver if 'is_org_approver' in locals() else False
                    )
            
            form.save()
            print(f"Form saved with status: {form.status}, decision: {form.decision}")  # Debug print
            return redirect('admin_dashboard')
        except Exception as e:
            print(f"Error processing form: {str(e)}")  # Debug print
            messages.error(request, f'Error processing request: {str(e)}')
            return render(request, 'ums/review_special.html', {'form': form})
    
    # Get organizational context for template
    org_context = None
    if form.organizational_unit:
        ancestors = []
        if hasattr(form.organizational_unit, 'get_ancestors'):
            ancestors = form.organizational_unit.get_ancestors()
            
        org_context = {
            'unit': form.organizational_unit,
            'ancestors': ancestors
        }
    
    return render(request, 'ums/review_special.html', {
        'form': form,
        'org_context': org_context
    })

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

# Organization Management Views
@role_required(["Admin"])
def organization_list(request):
    """View to list all organizational units"""
    organizations = OrganizationalUnit.objects.all()
    return render(request, "ums/organization_list.html", {"organizations": organizations})

@role_required(["Admin"])
def organization_create(request):
    """View to create a new organizational unit"""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        parent_id = request.POST.get("parent")
        
        if not name:
            messages.error(request, "Organization name is required")
            return redirect("organization_create")
        
        try:
            parent = None
            if parent_id:
                parent = OrganizationalUnit.objects.get(id=parent_id)
                
            OrganizationalUnit.objects.create(
                name=name,
                description=description,
                parent=parent
            )
            messages.success(request, f"Organization '{name}' created successfully")
            return redirect("organization_list")
        except Exception as e:
            messages.error(request, f"Error creating organization: {str(e)}")
    
    # Get all organizations for parent selection
    organizations = OrganizationalUnit.objects.all()
    return render(request, "ums/organization_form.html", {"organizations": organizations})

@role_required(["Admin"])
def organization_edit(request, org_id):
    """View to edit an organizational unit"""
    organization = get_object_or_404(OrganizationalUnit, id=org_id)
    
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        parent_id = request.POST.get("parent")
        
        if not name:
            messages.error(request, "Organization name is required")
            return redirect("organization_edit", org_id=org_id)
        
        try:
            # Update the organization
            organization.name = name
            organization.description = description
            
            # Handle parent organization
            if parent_id and parent_id != str(organization.id):  # Prevent self-parenting
                organization.parent = OrganizationalUnit.objects.get(id=parent_id)
            elif not parent_id:
                organization.parent = None
                
            organization.save()
            messages.success(request, f"Organization '{name}' updated successfully")
            return redirect("organization_list")
        except Exception as e:
            messages.error(request, f"Error updating organization: {str(e)}")
    
    # Get all organizations for parent selection, excluding self and descendants
    descendants = []
    if hasattr(organization, 'get_descendants'):
        descendants = organization.get_descendants(include_self=True)
    potential_parents = OrganizationalUnit.objects.exclude(
        id__in=[d.id for d in descendants] if descendants else [organization.id]
    )
    
    return render(request, "ums/organization_form.html", {
        "organization": organization,
        "organizations": potential_parents,
        "is_edit": True
    })

@role_required(["Admin"])
def organization_view(request, org_id):
    """View details of a specific organizational unit"""
    organization = get_object_or_404(OrganizationalUnit, id=org_id)
    
    # Get users assigned to this organization
    assigned_users = UserOrganizationAssignment.objects.filter(
        organizational_unit=organization
    ).select_related('user')
    
    # Get child organizations
    children = []
    if hasattr(organization, 'get_children'):
        children = organization.get_children()
    
    # Get parent organization path
    ancestors = []
    if hasattr(organization, 'get_ancestors'):
        ancestors = organization.get_ancestors()
    
    context = {
        "organization": organization,
        "assigned_users": assigned_users,
        "children": children,
        "ancestors": ancestors,
    }
    
    return render(request, "ums/organization_detail.html", context)

@role_required(["Admin"])
def organization_hierarchy(request):
    """View the full organizational hierarchy"""
    # Get all root nodes (organizations without parents)
    root_nodes = OrganizationalUnit.objects.filter(parent=None)
    
    # For each root node, get the full tree
    trees = []
    for root in root_nodes:
        tree = []
        if hasattr(root, 'get_descendants'):
            tree = root.get_descendants(include_self=True)
        trees.append({
            'root': root,
            'tree': tree
        })
    
    return render(request, "ums/organization_hierarchy.html", {"trees": trees})

# User Assignment Views
@role_required(["Admin"])
def assign_user_to_org(request):
    """View to assign users to organizational units"""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        org_id = request.POST.get("organization_id")
        is_approver = request.POST.get("is_approver") == "on"
        is_org_approver = request.POST.get("is_organizational_approver") == "on"
        
        if not user_id or not org_id:
            messages.error(request, "Both user and organization must be selected")
            return redirect("assign_user_to_org")
        
        try:
            user = Users.objects.get(id=user_id)
            organization = OrganizationalUnit.objects.get(id=org_id)
            
            # Check if assignment already exists
            assignment, created = UserOrganizationAssignment.objects.get_or_create(
                user=user,
                organizational_unit=organization,
                defaults={
                    'is_approver': is_approver,
                    'is_organizational_approver': is_org_approver
                }
            )
            
            if not created:
                # Update existing assignment
                assignment.is_approver = is_approver
                assignment.is_organizational_approver = is_org_approver
                assignment.save()
                messages.success(request, f"Updated {user.name}'s assignment to {organization.name}")
            else:
                messages.success(request, f"Assigned {user.name} to {organization.name}")
                
            return redirect("organization_users", org_id=org_id)
        
        except Exception as e:
            messages.error(request, f"Error assigning user: {str(e)}")
    
    users = Users.objects.filter(status="Active").order_by("name")
    organizations = OrganizationalUnit.objects.all().order_by("name")
    
    return render(request, "ums/assign_user_form.html", {
        "users": users,
        "organizations": organizations
    })

@role_required(["Admin"])
def user_organizations(request, user_id):
    """View to manage all organizations for a specific user"""
    user = get_object_or_404(Users, id=user_id)
    
    # Get all assignments for this user
    assignments = UserOrganizationAssignment.objects.filter(
        user=user
    ).select_related('organizational_unit')
    
    # If removing an assignment
    if request.method == "POST" and request.POST.get("action") == "remove":
        assignment_id = request.POST.get("assignment_id")
        try:
            assignment = UserOrganizationAssignment.objects.get(id=assignment_id, user=user)
            org_name = assignment.organizational_unit.name
            assignment.delete()
            messages.success(request, f"Removed {user.name} from {org_name}")
        except Exception as e:
            messages.error(request, f"Error removing assignment: {str(e)}")
        
        return redirect("user_organizations", user_id=user_id)
    
    # Get available organizations (not already assigned)
    assigned_org_ids = assignments.values_list('organizational_unit_id', flat=True)
    available_organizations = OrganizationalUnit.objects.exclude(
        id__in=assigned_org_ids
    ).order_by("name")
    
    return render(request, "ums/user_organizations.html", {
        "user": user,
        "assignments": assignments,
        "available_organizations": available_organizations
    })

@role_required(["Admin"])
def organization_users(request, org_id):
    """View to manage all users in a specific organization"""
    organization = get_object_or_404(OrganizationalUnit, id=org_id)
    
    # Get all user assignments for this organization
    assignments = UserOrganizationAssignment.objects.filter(
        organizational_unit=organization
    ).select_related('user')
    
    # If removing a user
    if request.method == "POST" and request.POST.get("action") == "remove":
        assignment_id = request.POST.get("assignment_id")
        try:
            assignment = UserOrganizationAssignment.objects.get(id=assignment_id, organizational_unit=organization)
            user_name = assignment.user.name
            assignment.delete()
            messages.success(request, f"Removed {user_name} from {organization.name}")
        except Exception as e:
            messages.error(request, f"Error removing user: {str(e)}")
        
        return redirect("organization_users", org_id=org_id)
    
    # Get available users (not already assigned to this organization)
    assigned_user_ids = assignments.values_list('user_id', flat=True)
    available_users = Users.objects.filter(
        status="Active"
    ).exclude(
        id__in=assigned_user_ids
    ).order_by("name")
    
    return render(request, "ums/organization_users.html", {
        "organization": organization,
        "assignments": assignments,
        "available_users": available_users
    })

# Approver Management Views
@role_required(["Admin"])
def approver_list(request):
    """View to list all approvers across the system"""
    # Get all user-organization assignments where user is an approver
    approver_assignments = UserOrganizationAssignment.objects.filter(
        Q(is_approver=True) | Q(is_organizational_approver=True)
    ).select_related('user', 'organizational_unit')
    
    # Group by user
    approvers_by_user = {}
    for assignment in approver_assignments:
        if assignment.user.id not in approvers_by_user:
            approvers_by_user[assignment.user.id] = {
                'user': assignment.user,
                'assignments': []
            }
        approvers_by_user[assignment.user.id]['assignments'].append(assignment)
    
    return render(request, "ums/approver_list.html", {
        "approvers": approvers_by_user.values()
    })

@role_required(["Admin"])
def manage_approver(request, user_id, org_id):
    """View to manage approver status for a user in an organization"""
    user = get_object_or_404(Users, id=user_id)
    organization = get_object_or_404(OrganizationalUnit, id=org_id)
    
    try:
        assignment = UserOrganizationAssignment.objects.get(user=user, organizational_unit=organization)
    except UserOrganizationAssignment.DoesNotExist:
        messages.error(request, f"{user.name} is not assigned to {organization.name}")
        return redirect("organization_users", org_id=org_id)
    
    if request.method == "POST":
        is_approver = request.POST.get("is_approver") == "on"
        is_org_approver = request.POST.get("is_organizational_approver") == "on"
        
        assignment.is_approver = is_approver
        assignment.is_organizational_approver = is_org_approver
        assignment.save()
        
        messages.success(request, f"Updated approver status for {user.name} in {organization.name}")
        return redirect("organization_users", org_id=org_id)
    
    return render(request, "ums/manage_approver.html", {
        "user": user,
        "organization": organization,
        "assignment": assignment
    })

