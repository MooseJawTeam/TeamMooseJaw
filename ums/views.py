import msal
from django.conf import settings
from django.shortcuts import redirect, render
from msal import ConfidentialClientApplication
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
import requests
from .models import Users
from .decorators import role_required
from django.contrib import messages



def index(request):
    return render(request, 'ums/welcome.html')

def user(request):
    if "user_id" not in request.session:
        return redirect("ums-login")
    user_data = {
        "name": request.session.get("user_name", "Unknown"),
        "email": request.session.get("user_email", "No Email"),
        "id": request.session.get("user_id", None),
        "role":request.session.get("user_role", "Basicuser")
    }

    return render(request, "ums/user.html", {"user": user_data})

@role_required(["Admin"])
def admin_dashboard(request):
    if request.session.get("user_role") != "Admin":
        return redirect("welcome")  # Redirect non-admins

    users = Users.objects.all()

    # Get logged-in admin user details
    admin_user = {
        "name": request.session.get("user_name", "Admin"),  # Default to "Admin" if not found
        "email": request.session.get("user_email", "No Email"),
        "id": request.session.get("user_id", None),
        "role": request.session.get("user_role", "Admin"),
    }

    if request.method == 'POST':
        if 'save' in request.POST and request.POST.get('save'):  # Update user details
            user_id = request.POST.get('save')
            user = Users.objects.get(id=user_id)
            user.name = request.POST['name']
            user.email = request.POST['email']
            user.status = request.POST['status']
            user.role = request.POST['role']
            user.save()

        elif 'add_user' in request.POST:  # Add a new user
            name = request.POST['name']
            email = request.POST['email']
            role = request.POST.get("role", "Basicuser")
            status = request.POST.get("status", "Active")

            if name and email:
                user = Users(name=name, email=email, role=role, status=status)
                user.save()

        elif 'delete' in request.POST:  # Delete a user
            user_id = request.POST.get('delete')
            Users.objects.filter(id=user_id).delete()

        elif 'deactivate' in request.POST:  # Deactivate a user
            user_id = request.POST.get('deactivate')
            user = Users.objects.get(id=user_id)
            user.status = "Inactive"
            user.save()

        elif 'activate' in request.POST:  # Reactivate a user
            user_id = request.POST.get('activate')
            user = Users.objects.get(id=user_id)
            user.status = "Active"
            user.save()

        return redirect("admin_dashboard")  # Refresh the page

    return render(request, 'ums/admin.html', {'users': users, 'admin_user': admin_user})

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

from django.contrib import messages

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

        if user.role == "Admin":
            return redirect("admin_dashboard")
        return redirect("user")

    except Exception as e:
        messages.error(request, f"Error in authentication: {str(e)}")
        return redirect("ums-login")

def logout(request):
    request.session.flush() # clear session
    return redirect("/")
