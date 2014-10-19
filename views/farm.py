# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from world.models import *
from resources.Evopic import Evopic
from resources import mutation, breed
import json
from django.forms.models import model_to_dict

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
            living_evopix = Evopix.objects.filter(health__gt=0)
            output = []
            for evopic in living_evopix:
                evo = Evopic(evopic.zeroed_evp)
                output.append({"id": evopic.evo_id, "svg": evo.svg_out(scale=0.1)})
                landunits = LandUnit.objects.filter(evopic_id=evopic.evo_id)
                min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
                for landunit in landunits:
                    min_x = landunit.x if landunit.x < min_x else min_x
                    min_y = landunit.y if landunit.y < min_y else min_y
                    max_x = landunit.x if landunit.x > max_x else max_x
                    max_y = landunit.y if landunit.y > max_y else max_y

                output[-1]["min_x"] = min_x
                output[-1]["min_y"] = min_y
                output[-1]["max_x"] = max_x
                output[-1]["max_y"] = max_y

            return HttpResponse(json.dumps(output))

        evp = request.POST.get('evp', '')
        bob = mutation.mutate(Evopic(evp))
        return HttpResponse("Blahh")

    else:
        db_evopix = LandUnit.objects.filter(evopic_id="1")

        return HttpResponse(db_evopix[0])

