from django.http import HttpResponse
from .models import Users
from django.shortcuts import render

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
    return render(request, 'ums/dashboard.html', {})

def admin(request):
    return render(request, 'ums/admin.html', {})
