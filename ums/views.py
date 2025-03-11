<<<<<<< HEAD
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
        return redirect("login")
    user_data = {
        "name": request.session.get("user_name", "Unknown"),
        "email": request.session.get("user_email", "No Email"),
        "id": request.session.get("user_id", None),
        "role":request.session.get("user_role", "Basicuser")
    }

    return render(request, "ums/user.html", {"user": user_data, 'admin_user':admin_user})

@role_required(["Admin"])
def admin_dashboard(request):
    if request.session.get("user_role") != "Admin":
        return redirect("home")  # Redirect non-admins

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
        return redirect("login")

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
            return redirect("login")

        # Fetch user details from Microsoft Graph API
        headers = {"Authorization": f'Bearer {token_response["access_token"]}'}
        user_data = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()

        user_id = user_data.get("id", None)
        user_email = user_data.get("mail", None) or user_data.get("userPrincipalName", None)

        if not user_id or not user_email:
            messages.error(request, "Your Microsoft account is missing an email. Contact support.")
            return redirect("login")

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
        return redirect("login")

def logout(request):
    request.session.flush() # clear session
    return redirect("/")


=======
from django.http import HttpResponse
from .models import Users
from django.shortcuts import render,get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def index(request):
    return render(request, 'ums/welcome.html', {})
#    a return HttpResponse("Hello, world. You're at the ums index.")

# 2025-02-20T17:57:24.227204272Z: [INFO]  X-Ms-Client-Principal-Name:congouya@CougarNet.UH.EDU
# 2025-02-20T17:57:24.227208424Z: [INFO]  X-Ms-Client-Principal-Id:41216345-d292-45aa-866b-dac98917256f


def user(request):
    print('Headers')
    for key, value in request.headers.items():
        print(f"{key}:{value}")

    logged_in_user =  get_logged_in_user(request)
    return render(request, 'ums/user.html', {'userID': logged_in_user})


def admin(request):

#     appServiceAuthSession = request.COOKIES['AppServiceAuthSession']
#     # send this to a MSFT API with requests
    
    users = Users.objects.all()
    logged_in_user = get_logged_in_user(request)

#     if logged_in_user.role !=git  'Admin':
#         return HttpResponse('Unauthorized', status=401)

    print(logged_in_user)

    if request.method == 'POST':
        if 'save' in request.POST and request.POST.get('save'):
            userid = request.POST.get('save')
            user = Users.objects.get(id=userid)
            print(request.POST['name'])
            user.name = request.POST['name']
            user.email = request.POST['email']
            user.status = request.POST['status']
            user.save()

        elif 'save' in request.POST:
            name = request.POST['name']
            email = request.POST['email']
            status = request.POST['status']
            if name and email:
                user = Users(name=name, email=email, status=status)
                user.save()

        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            deleteuser = Users.objects.get(id=pk)
            deleteuser.delete()

    return render(request, 'ums/admin.html', {'users':users, 'userID': logged_in_user,})

# post = Post.objects.create(title="Test", body="abc")

# 2025-02-20T17:57:24.227204272Z: [INFO]  X-Ms-Client-Principal-Name:congouya@CougarNet.UH.EDU
# 2025-02-20T17:57:24.227208424Z: [INFO]  X-Ms-Client-Principal-Id:41216345-d292-45aa-866b-dac98917256f
def get_logged_in_user(request):
    id = request.headers['X-Ms-Client-Principal-Id']
    email = request.headers['X-Ms-Client-Principal-Name']
    print(f"USING id: {id}")
    
    user = Users.objects.filter(id=id).first()
    if user:
        print("FOUND A USER!")
        return user
    else:
        print("DID NOT FIND A USER")
        user = Users(name='',email=email,id=id, status='active',role='Admin')
        user.save()
        print(f"SAVED NEW USER: {user.id}")
        return user
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891
