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
        min_x = int(request.POST.get("min_x", ""))
        min_y = int(request.POST.get("min_y", ""))
        max_x = int(request.POST.get("max_x", ""))
        max_y = int(request.POST.get("max_y", ""))
        evopix = LandUnit.objects.filter(evopic_id=1, x__gte=min_x, x__lte=max_x, y__gte=min_y, y__lte=max_y)
        Evopix.objects.filter(health__gt=0)
        output = []
        for evopic in evopix:
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

    else:
        return HttpResponse("Fail")


def _move():
    def look(x_depth, y_depth):
        output = {"fences": {"top": [], "bottom": [], "left": [], "right": []}, "evopix": [], "self": []}

        # Get info on the land units within depth field
        new_landunits = LandUnit.objects.filter(y__gte=(min_y + min([0, y_depth])),
                                                y__lte=(max_y + max([0, y_depth])),
                                                x__gte=(min_x + min([0, x_depth])),
                                                x__lte=(max_x + max([0, x_depth])))

        for landunit in new_landunits:
            if landunit.evopic_id and \
                    (min_x > landunit.x or max_x < landunit.x or min_y > landunit.y or max_y < landunit.y):
                output["evopix"].append((landunit.evopic_id, landunit.x, landunit.y))
            elif landunit.evopic:
                output["self"].append((landunit.x, landunit.y))

            if landunit.t_fence_id:
                output["fences"]["top"].append((landunit.x, landunit.y))
            if landunit.b_fence_id:
                output["fences"]["bottom"].append((landunit.x, landunit.y))
            if landunit.l_fence_id:
                output["fences"]["left"].append((landunit.x, landunit.y))
            if landunit.r_fence_id:
                output["fences"]["right"].append((landunit.x, landunit.y))

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

    # List of all possible fences that would prevent the selected evopic from moving
    blocking_fences = {"bottom": [], "right": [], "left": [], "top": []}
    # Fences directly adjacent to the evopic, above or below
    for x in range(min_x, max_x):
        blocking_fences["top"].append((x, max_y))
        blocking_fences["bottom"].append((x, min_y))
    # Edge-on fences in the space above or below the evopic
    for i in range(max_x - min_x):  # Don't need to include 'left' fences because they are contained in 'right'
        blocking_fences["right"].append((min_x + i, max_y + 1))
        blocking_fences["right"].append((min_x + i, max_y - 1))
    # Fences directly adjacent to the evopic, on either side
    for y in range(min_y, max_y):
        blocking_fences["right"].append((max_x, y))
        blocking_fences["left"].append((min_x, y))
    # Edge-on fences in the space left or right of the evopic
    for i in range(max_y - min_y):  # Don't need to include 'bottom' fences because they are contained in 'top'
        blocking_fences["top"].append((max_x + 1, min_y + i))
        blocking_fences["top"].append((max_x - 1, min_y + i))

    direction = choice(["up", "down", "left", "right"])
    if direction == "up":
        neighborhood = look(0, 1)
        for unit in neighborhood["fences"]["top"]:
            if unit in blocking_fences["top"]:
                return "Fences above"
        for unit in neighborhood["fences"]["right"]:
            if unit in blocking_fences["right"]:
                return "Fence in adjacent cells above"

        new_landunits = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
        old_landunits = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)

    elif direction == "down":
        neighborhood = look(0, -1)
        for unit in neighborhood["fences"]["bottom"]:
            if unit in blocking_fences["bottom"]:
                return "Fences below"
        for unit in neighborhood["fences"]["right"]:
            if unit in blocking_fences["right"]:
                return "Fence in adjacent cells below"

        new_landunits = LandUnit.objects.filter(y=min_y - 1, x__gte=min_x, x__lte=max_x)
        old_landunits = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)

    elif direction == "right":
        neighborhood = look(1, 0)
        for unit in neighborhood["fences"]["right"]:
            if unit in blocking_fences["right"]:
                return "Fence to right"
        for unit in neighborhood["fences"]["top"]:
            if unit in blocking_fences["top"]:
                return "Fence in adjacent cells to right"

        new_landunits = LandUnit.objects.filter(x=max_x + 1, y__gte=min_y, y__lte=max_y)
        old_landunits = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)

    else:  # direction == 'left'
        neighborhood = look(-1, 0)
        for unit in neighborhood["fences"]["left"]:
            if unit in blocking_fences["left"]:
                return "Fence to left"
        for unit in neighborhood["fences"]["top"]:
            if unit in blocking_fences["top"]:
                return "Fence in adjacent cells to left"

        new_landunits = LandUnit.objects.filter(x=min_x - 1, y__gte=min_y, y__lte=max_y)
        old_landunits = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)

    if len(neighborhood["evopix"]) > 0:
        evopic = Evopix.objects.filter(evo_id=evo_id).get().evp
        mate = Evopix.objects.filter(evo_id=choice(neighborhood["evopix"])[0]).get().evp
        breed(evopic, mate)
        return "Breeding"

    else:
        new_landunits.update(evopic_id=evo_id)
        old_landunits.update(evopic_id=None)
        return "Evo %s moving %s" % (evo_id, direction)


def move(request):
    try_move = _move()
    return HttpResponse(try_move)
#-------------------------Sandbox-------------------------------#
def run():
    print(_move())