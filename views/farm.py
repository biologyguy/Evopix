from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *


# Create your views here.
def welcome(request):
    bob = Evopix.objects.all()[0]
    return HttpResponse("Hello, my evopix' name is %s" % bob.name)