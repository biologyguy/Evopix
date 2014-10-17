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
        output = {"svg": bob.svg_out(bounding_box=325), "evp": bob.evp}
        for i in range(1, 9):
            baby = mutation.mutate(Evopic(evp))
            baby = Evopic(breed.zero_evp(baby.evp))
            output["svg%s" % i] = baby.svg_out(bounding_box=180)
            output["evp%s" % i] = baby.evp

        return render(request, 'templates/404.html', output)

    else:
        bob = Evopic(Evopix.objects.all()[1].zeroed_evp)
        return render(request, 'templates/404.html', {"svg": bob.svg_out(), "evp": bob.evp})


def mutate(request):
    if request.method == "POST":
        evp = request.POST.get('evp', '')
        bob = mutation.mutate(Evopic(evp))
        return HttpResponse(bob.svg_out())

    else:

        return HttpResponse("Dead...")