from django.http import HttpResponse
from .models import Users
from django.shortcuts import render,get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def index(request):
    return render(request, 'ums/welcome.html', {})
#    a return HttpResponse("Hello, world. You're at the ums index.")


def user(request):
    print('Headers')
    for key, value in request.headers.items():
        print(f"{key}:{value}")

    logged_in_user =  get_logged_in_user()

    return render(request, 'ums/user.html', {'userID': logged_in_user})


def admin(request):

#     appServiceAuthSession = request.COOKIES['AppServiceAuthSession']
#     # send this to a MSFT API with requests
    
    users = Users.objects.all()


    
    logged_in_user = get_logged_in_user()

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



def get_logged_in_user():
    return Users.objects.get(id=1)