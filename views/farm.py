# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from resources.Evopic import Evopic


# Create your views here.
def welcome(request):
    return render(request, 'templates/welcome.html')


def bob(request):
    bob_db = Evopic(Evopix.objects.get(evo_id=1).zeroed_evp)
    return HttpResponse(bob_db.svg_out())


def farm(request):
    return render(request, 'templates/farm.html')