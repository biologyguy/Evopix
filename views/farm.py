# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from evp.models import *
from world.models import *
from resources.Evo import Evopic
from resources import mutation
from resources.breed import *
import json
from random import choice
import MyFuncs

# Create your views here.
def welcome(request):
    return render(request, 'templates/welcome.html')


def bob(request):
    bob_db = Evopic(Evopix.objects.get(evo_id=1).evp)
    return HttpResponse(bob_db.svg_out())


def farm(request):
    bob = Evopic(Evopix.objects.all()[1].evp)
    return render(request, 'templates/farm.html', {"svg": bob.svg_out(), "evp": bob.evp})


# AJAX called functions below here.
def populate_map(request):
    if request.method == "POST":
        if not request.POST.get('evp', ''):
            living_evopix = Evopix.objects.filter(health__gt=0)
            output = []
            for evopic in living_evopix:
                bob = Evopic(evopic.evp)
                output.append({"id": evopic.evo_id})
                landunits = LandUnit.objects.filter(evopic_id=evopic.evo_id)
                min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
                for landunit in landunits:
                    min_x = landunit.x if landunit.x < min_x else min_x
                    min_y = landunit.y if landunit.y < min_y else min_y
                    max_x = landunit.x if landunit.x > max_x else max_x
                    max_y = landunit.y if landunit.y > max_y else max_y

                size_x = (max_x - min_x + 1) * 50
                size_y = (max_y - min_y + 1) * 50
                output[-1]["svg"] = bob.svg_out(scale=0.1, bounding_box=(size_x, size_y))
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


def _move():
    def look(x_depth, y_depth):
        output = {"fences": {"top": [], "bottom": [], "left": [], "right": []}, "evopix": []}

        # Get info on the land units within depth field
        new_landunits = LandUnit.objects.filter(y__gte=(min_y + min([0, y_depth])),
                                                y__lte=(max_y + max([0, y_depth])),
                                                x__gte=(min_x + min([0, x_depth])),
                                                x__lte=(max_x + max([0, x_depth])))
        for landunit in new_landunits:
            if landunit.t_fence_id:
                output["fences"]["top"].append(landunit.land_id)
            if landunit.b_fence_id:
                output["fences"]["bottom"].append(landunit.land_id)
            if landunit.l_fence_id:
                output["fences"]["left"].append(landunit.land_id)
            if landunit.r_fence_id:
                output["fences"]["right"].append(landunit.land_id)
            if landunit.evopic and \
                    (min_x > landunit.x or max_x < landunit.x) and (min_y > landunit.y or max_y < landunit.y):
                output["evopix"].append(landunit.evopic_id)

        output["fences"]["top"] = False if len(output["fences"]["top"]) != 0 else output["fences"]["top"]
        output["fences"]["bottom"] = False if len(output["fences"]["bottom"]) != 0 else output["fences"]["bottom"]
        output["fences"]["right"] = False if len(output["fences"]["right"]) != 0 else output["fences"]["right"]
        output["fences"]["left"] = False if len(output["fences"]["left"]) != 0 else output["fences"]["left"]
        output["evopix"] = False if len(output["evopix"]) != 0 else output["evopix"]
        return output

    living_evopix = Evopix.objects.filter(health__gt=0)
    evo_id = choice(living_evopix).evo_id
    landunits = LandUnit.objects.filter(evopic_id=evo_id)
    min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
    for landunit in landunits:
        min_x = landunit.x if landunit.x < min_x else min_x
        min_y = landunit.y if landunit.y < min_y else min_y
        max_x = landunit.x if landunit.x > max_x else max_x
        max_y = landunit.y if landunit.y > max_y else max_y

    direction = choice(["up", "down", "left", "right"])
    if direction == "up":
        neighborhood = look(0, 1)
        if neighborhood["fences"]["left"] or neighborhood["fences"]["right"] or neighborhood["fences"]["bottom"]:
            return False
        else:
            new_landunits = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
            old_landunits = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)

    elif direction == "down":
        neighborhood = look(0, -1)
        if neighborhood["fences"]["left"] or neighborhood["fences"]["right"] or neighborhood["fences"]["top"]:
            return False
        else:
            new_landunits = LandUnit.objects.filter(y=min_y - 1, x__gte=min_x, x__lte=max_x)
            old_landunits = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)

    elif direction == "right":
        neighborhood = look(1, 0)
        if neighborhood["fences"]["left"] or neighborhood["fences"]["top"] or neighborhood["fences"]["bottom"]:
            return False
        else:
            new_landunits = LandUnit.objects.filter(x=max_x + 1, y__gte=min_y, y__lte=max_y)
            old_landunits = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)

    else:  # direction == 'left'
        neighborhood = look(-1, 0)
        if neighborhood["fences"]["right"] or neighborhood["fences"]["top"] or neighborhood["fences"]["bottom"]:
            return False
        else:
            new_landunits = LandUnit.objects.filter(x=min_x - 1, y__gte=min_y, y__lte=max_y)
            old_landunits = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)

    if neighborhood["evopix"]:
        evopic = Evopix.objects.filter(evp_id=evo_id).get().evp
        mate = Evopix.objects.filter(land_id=choice(neighborhood["evopix"])).get().evp
        breed(evopic, mate)
        return True

    else:
        new_landunits.update(evopic_id=evo_id)
        old_landunits.update(evopic_id=None)
        return True


def move(request):
    return HttpResponse(_move())
#-------------------------Sandbox-------------------------------#
def run():
    _move()