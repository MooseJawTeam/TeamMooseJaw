from django.http import HttpResponse
from .models import Users
from django.shortcuts import render,get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.conf import settings
from .ms_graph import get_access_token, get_user_info

# # Create your views here.
def index(request):
    return render(request, 'ums/welcome.html', {})
#    a return HttpResponse("Hello, world. You're at the ums index.")

# # 2025-02-20T17:57:24.227204272Z: [INFO]  X-Ms-Client-Principal-Name:congouya@CougarNet.UH.EDU
# # 2025-02-20T17:57:24.227208424Z: [INFO]  X-Ms-Client-Principal-Id:41216345-d292-45aa-866b-dac98917256f
#
#
# def user(request):
#     print('Headers')
#     for key, value in request.headers.items():
#         print(f"{key}:{value}")
#
#     logged_in_user =  get_logged_in_user(request)
#
#     return render(request, 'ums/user.html', {'userID': logged_in_user})
#
#
# def admin(request):
#
# #     appServiceAuthSession = request.COOKIES['AppServiceAuthSession']
# #     # send this to a MSFT API with requests
#
#     users = Users.objects.all()
#
#     logged_in_user = get_logged_in_user(request)
#
# #     if logged_in_user.role !=git  'Admin':
# #         return HttpResponse('Unauthorized', status=401)
#
#     print(logged_in_user)
#
#     if request.method == 'POST':
#
#         if 'save' in request.POST and request.POST.get('save'):
#             userid = request.POST.get('save')
#             user = Users.objects.get(id=userid)
#             print(request.POST['name'])
#             user.name = request.POST['name']
#             user.email = request.POST['email']
#             user.status = request.POST['status']
#             user.save()
#
#
#         elif 'save' in request.POST:
#             name = request.POST['name']
#             email = request.POST['email']
#             status = request.POST['status']
#             if name and email:
#                 user = Users(name=name, email=email, status=status)
#                 user.save()
#
#         elif 'delete' in request.POST:
#             pk = request.POST.get('delete')
#             deleteuser = Users.objects.get(id=pk)
#             deleteuser.delete()
#
#     return render(request, 'ums/admin.html', {'users':users, 'userID': logged_in_user,})
#
# # post = Post.objects.create(title="Test", body="abc")
#
# # 2025-02-20T17:57:24.227204272Z: [INFO]  X-Ms-Client-Principal-Name:congouya@CougarNet.UH.EDU
# # 2025-02-20T17:57:24.227208424Z: [INFO]  X-Ms-Client-Principal-Id:41216345-d292-45aa-866b-dac98917256f
# def get_logged_in_user(request):
#     id = request.headers['X-Ms-Client-Principal-Id']
#     email = request.headers['X-Ms-Client-Principal-Name']
#     print(f"USING id: {id}")
#     user = Users.objects.filter(id=id).first()
#     if user is not None:
#         print("FOUND A USER!")
#         return user
#     else:
#         print("DID NOT FIND A USER")
#         user = Users(name='',email=email,id=id, status='active',role='Admin')
#         user.save()
#         print(f"SAVED NEW USER: {user.id}")
#         return user

def login(request):
    """Redirect users to Microsoft login"""
    auth_url = f"{settings.MICROSOFT_AUTH['AUTHORITY']}/oauth2/v2.0/authorize"
    params = {
        "client_id": settings.MICROSOFT_AUTH["CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": settings.MICROSOFT_AUTH["REDIRECT_URI"],
        "scope": " ".join(settings.MICROSOFT_AUTH["SCOPES"]),
        "response_mode": "query"
    }
    return redirect(f"{auth_url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}")

def auth_callback(request):
    """Handle OAuth callback and retrieve user info"""
    print('a')
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "No authorization code received"}, status=400)

    # Exchange code for token
    print('b')
    access_token = get_access_token()

    if not access_token:
        return JsonResponse({"error": "Authentication failed"}, status=400)

    # Fetch user profile
    user_data = get_user_info(access_token)

    if not user_data:
        return JsonResponse({"error": "Failed to retrieve user data"}, status=400)

    # Process user info
    user_id = user_data["id"]
    user_email = user_data["mail"] or user_data["userPrincipalName"]
    user_name = user_data.get("displayName", "")

    # Check if user exists in the database
    from users.models import Users
    user, created = Users.objects.get_or_create(
        id=user_id,
        defaults={"name": user_name, "email": user_email, "role": "basicuser"}
    )

    # Store user session
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email

    return redirect("dashboard")
