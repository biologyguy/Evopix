# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from world.models import *
from resources.Evopic import Evopic
from resources import mutation, breed

# Create your views here.
def welcome(request):
    return render(request, 'templates/welcome.html')


def bob(request):
    bob_db = Evopic(Evopix.objects.get(evo_id=1).zeroed_evp)
    return HttpResponse(bob_db.svg_out())


def farm(request):
    bob = Evopic(Evopix.objects.all()[1].zeroed_evp)
    return render(request, 'templates/farm.html', {"svg": bob.svg_out(), "evp": bob.evp})


# AJAX called functions below here.
def mutate(request):
    if request.method == "POST":
        if not request.POST.get('evp', ''):
            return HttpResponse("nothing")

        evp = request.POST.get('evp', '')
        bob = mutation.mutate(Evopic(evp))
        return HttpResponse("Blahh")

    else:

        return HttpResponse("Dead...")

