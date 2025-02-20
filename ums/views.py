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
    email = request.headers['X-Ms-Client-Principal-Name']
    print(f"USING EMAIL: {email}")
    email = "qux@baz.com"
    user = Users.objects.filter(email=email).first()
    if not None:
        print("FOUND A USER!")
        return user
    else:
        print("DID NOT FIND A USER")
        user = Users(name='foo bar',email=email,status='active')
        user.save()
        print(f"SAVED NEW USER: {user.id}")
        return user
