# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from resources.Evopic import Evopic
from resources import mutation, breed


# Create your views here.
def index(request):
    bob = Evopic(Evopix.objects.get(evo_id=1).zeroed_evp)
    list_of_stuff = ["Juice", 23, {"name": "Joe", "age": 98}]
    return render(request, 'templates/index.html', {"bob": bob.svg_out(), "list_of_stuff": list_of_stuff})


def not_found(request):
    if request.method == "POST":
        evp = request.POST.get('evp', '')
        bob = Evopic(evp)
        bob = mutation.mutate(bob)
        baby = Evopic(breed.zero_evp(bob.evp))

    else:
        bob = Evopic(Evopix.objects.all()[1].evp)
        bob = mutation.mutate(bob)
        baby = Evopic(breed.zero_evp(bob.evp))

    return render(request, 'templates/404.html', {"svg": baby.svg_out(), "evp": baby.evp})