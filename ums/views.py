from django.http import HttpResponse
from .models import Users
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def index(request):
    data = Users.objects.all()
    data1 = data[0]
    name1 = data1.name
    data2 = data[1]
    name2 = data2.name

    object1 = 'here is the name of the first user in the table:'
    object1 += '<ul>'
    object1 += '<li>' + name1 + '</li>'
    object1 += '<li>' + name2 + '</li>'
    object1 += '</ul>'

    return HttpResponse(object1)
#    a return HttpResponse("Hello, world. You're at the ums index.")


def dashboard(request):

    logged_in_user =  get_logged_in_user()

    return render(request, 'ums/dashboard.html', {'userID': logged_in_user})


def admin(request):
    
    users = Users.objects.all()
    
    logged_in_user = get_logged_in_user()

    print(logged_in_user)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']

        if name and email:
            user = Users(name=name, email=email)
            user.save()
   

    return render(request, 'ums/admin.html', {'users':users, 'userID': logged_in_user,})


def get_logged_in_user():
    return Users.objects.get(id=1)