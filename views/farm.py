# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from resources.Evo import Evopic
from evp.models import *
from world.models import *
from resources.breed import *
import json
import traceback
from django.contrib.auth.decorators import login_required


# Support functions
def find_min_max(landunits):
    min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
    for landunit in landunits:
        min_x = landunit.x if landunit.x < min_x else min_x
        min_y = landunit.y if landunit.y < min_y else min_y
        max_x = landunit.x if landunit.x > max_x else max_x
        max_y = landunit.y if landunit.y > max_y else max_y
    return [min_x, min_y, max_x, max_y]


# Create your views here.
def welcome(request):
    return render(request, 'templates/welcome.html')


def bob(request):
    bob_db = Evopic(Evopix.objects.get(evo_id=1).evp)
    return HttpResponse(bob_db.svg_out())


@login_required
def farm(request):
    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        return HttpResponse("Something has gone wrong... Can't find your user name in farm view.")
    midpoint = UserInfo.objects.filter(user_id=user_id)[0].farm_midpoint_id
    midpoint = LandUnit.objects.filter(land_id=midpoint)[0]

    min_x, min_y, max_x, max_y = midpoint.x - 5, midpoint.y - 5, midpoint.x + 5, midpoint.y + 5

    return render(request, 'templates/farm.html', {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y})


# AJAX called functions below here.
def populate_map(request):
    max_allowable_data = 40

    try:
        if request.method == "POST":
            min_x = int(request.POST.get("min_x", ""))
            min_y = int(request.POST.get("min_y", ""))
            max_x = int(request.POST.get("max_x", ""))
            max_y = int(request.POST.get("max_y", ""))

            # fail if someone trys to get more data than I want them to get...
            if max_x - min_x > max_allowable_data or max_y - min_y > max_allowable_data:
                return HttpResponse("Nope, not going to give you that much of the world... Sorry.")

            landunits = LandUnit.objects.filter(evopic_id__gte=1, x__gte=min_x, x__lte=max_x, y__gte=min_y, y__lte=max_y)

            evo_ids = []
            for landunit in landunits:
                if landunit.evopic_id in evo_ids:
                    continue
                else:
                    evo_ids.append(landunit.evopic_id)

            output = []
            for evo_id in evo_ids:
                bob = Evopic(Evopix.objects.filter(evo_id=evo_id).get().evp)
                output.append({"id": evo_id})

                landunits = LandUnit.objects.filter(evopic_id=evo_id)
                min_x, min_y, max_x, max_y = find_min_max(landunits)

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
    except:
        typ, value, tback = sys.exc_info()
        print("Error caught! %s" % traceback.print_tb(tback))
        return HttpResponse("Fail")


#-------------------------Sandbox-------------------------------#
def run():
    print()