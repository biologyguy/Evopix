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
            live_evopic_ids = []
            for evopic in living_evopix:
                live_evopic_ids.append(evopic.evo_id)

            move(live_evopic_ids)
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

def move(live_evopic_ids):
    def check_land_occupied(land_units):
        for landunit in land_units:
            if landunit.evopic_id:
                return landunit.evopic_id
        return False

    evo_id = choice(live_evopic_ids)
    landunits = LandUnit.objects.filter(evopic_id=evo_id)
    min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
    for landunit in landunits:
        min_x = landunit.x if landunit.x < min_x else min_x
        min_y = landunit.y if landunit.y < min_y else min_y
        max_x = landunit.x if landunit.x > max_x else max_x
        max_y = landunit.y if landunit.y > max_y else max_y

    direction = choice(["up", "down", "left", "right"])

    if direction == "up":
        new_landunits = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)
        for landunit in new_landunits:
            if landunit.t_fence_id:
                return False

        new_landunits = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
        check = check_land_occupied(new_landunits)
        if not check:
            old_landunits = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)

    elif direction == "down":
        new_landunits = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)
        for landunit in new_landunits:
            if landunit.b_fence_id:
                return False

        new_landunits = LandUnit.objects.filter(y=min_y - 1, x__gte=min_x, x__lte=max_x)
        check = check_land_occupied(new_landunits)
        if not check:
            old_landunits = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)

    elif direction == "right":
        new_landunits = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)
        for landunit in new_landunits:
            if landunit.r_fence_id:
                return False

        new_landunits = LandUnit.objects.filter(x=max_x + 1, y__gte=min_y, y__lte=max_y)
        check = check_land_occupied(new_landunits)
        if not check:
            old_landunits = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)

    elif direction == "left":
        new_landunits = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)
        for landunit in new_landunits:
            if landunit.l_fence_id:
                return False
        new_landunits = LandUnit.objects.filter(x=min_x - 1, y__gte=min_y, y__lte=max_y)
        check = check_land_occupied(new_landunits)
        if not check:
            old_landunits = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)

    if check:
        mom = Evopic(Evopix.objects.filter(evp_id=evo_id).get())
        dad = Evopic(Evopix.objects.filter(evp_id=check).get())
        breed(mom, dad)
        return False

    else:
        new_landunits.update(evopic_id=evo_id)
        old_landunits.update(evopic_id=None)
        return True


#-------------------------Sandbox-------------------------------#
def run():
    print(move())