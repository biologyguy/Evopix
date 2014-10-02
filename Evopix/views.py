from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from resources.Evopic import Evopic


# Create your views here.
def index(request):
    return HttpResponse("Home page")


def not_found(request):
    bob = Evopic(Evopix.objects.all()[0].zeroed_evp)
    return HttpResponse("Sorry, the page you have requested was not found\n%s" % bob.svg_out())