# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse
from resources.Evo import Evopic
from evp.models import *
from world.models import *
from the_shop.models import *
from resources.breed import *
import json
import traceback
from django.contrib.auth.decorators import login_required

# magic numbers... need to keep track manually for now
world_size = {"x": 20, "y": 20}


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

    num_fences = 5
    num_breeding = 5

    tool_shed = "<ul><li>Fences: %s</li><li>Breeding pellets: %s</li></ul>" % (num_fences, num_breeding)

    return render(request, 'templates/farm.html', {"midpoint": midpoint.land_id, "tool_shed": {"fences": num_fences, "pellets": num_breeding}})

# Support functions
def find_min_max(landunits):
    min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
    for landunit in landunits:
        min_x = landunit.x if landunit.x < min_x else min_x
        min_y = landunit.y if landunit.y < min_y else min_y
        max_x = landunit.x if landunit.x > max_x else max_x
        max_y = landunit.y if landunit.y > max_y else max_y
    return [min_x, min_y, max_x, max_y]


def get_land(min_x, min_y, max_x, max_y):
    output = []
    land_types = {}
    land_types_q = LandTypes.objects.all()
    for land_type in land_types_q:
        land_types[land_type.type_id] = land_type.base_color

    fence_types = {}
    fence_types_q = Fences.objects.all()
    for fence in fence_types_q:
        fence_types[fence.fence_id] = {"horiz": fence.horiz_img_location, "vert": fence.vert_img_location}

    landunits_q = LandUnit.objects.filter(x__gte=min_x, x__lte=max_x, y__gte=min_y, y__lte=max_y)
    for landunit in landunits_q:
        output.append({"x": landunit.x, "y": landunit.y, "land_id": landunit.land_id,
                       "color": land_types[landunit.type_id]})

        if landunit.t_fence_id:
            output[-1]["horiz_fence"] = fence_types[landunit.t_fence_id]["horiz"]
        else:
            output[-1]["horiz_fence"] = None

        if landunit.r_fence_id:
            output[-1]["vert_fence"] = fence_types[landunit.r_fence_id]["vert"]
        else:
            output[-1]["vert_fence"] = None

    return output


def get_evopix(min_x, min_y, max_x, max_y, b_box_size, svg_scale_factor):
    output = []
    evo_ids = []
    landunits_q = LandUnit.objects.filter(x__gte=min_x, x__lte=max_x, y__gte=min_y, y__lte=max_y)
    for landunit in landunits_q:
        if landunit.evopic_id:
            if landunit.evopic_id not in evo_ids:
                evo_ids.append(landunit.evopic_id)

    for evo_id in evo_ids:
        evopic = Evopic(Evopix.objects.filter(evo_id=evo_id).get().evp)
        output.append({"id": evo_id})

        landunits_q = LandUnit.objects.filter(evopic_id=evo_id)
        min_x, min_y, max_x, max_y = find_min_max(landunits_q)

        size_x = (max_x - min_x + 1) * b_box_size
        size_y = (max_y - min_y + 1) * b_box_size
        output[-1]["svg"] = evopic.svg_out(scale=svg_scale_factor, bounding_box=(size_x, size_y))
        output[-1]["min_x"] = min_x
        output[-1]["min_y"] = min_y
        output[-1]["max_x"] = max_x
        output[-1]["max_y"] = max_y
    return output


# AJAX called functions below here.
# TODO!!!!!!!!!!
def extend_land(request):  # Only access the bits of land required if the frame moves
    try:
        if request.method == "POST":
            return
        else:
            print("Failed post.")
            return HttpResponse("Fail")
    except:
        typ, value, tback = sys.exc_info()
        print("Error caught! %s" % traceback.print_tb(tback))
        return HttpResponse("Fail")
# !!!!!!!!!!!

def populate_map(request):
    try:
        if request.method == "POST":
            output = {"land": [], "evopix": []}
            midpoint = int(request.POST.get("midpoint", ""))
            zoom = int(request.POST.get("zoom", ""))  # Currently only 1 zoom level (10) implemented

            midpoint = LandUnit.objects.filter(land_id=midpoint)[0]
            update_midpoint = False

            if zoom == 10:
                # Handel all the edge-of-world cases
                if not midpoint.x - 6 >= 1:
                    update_midpoint = True
                    min_x = 1
                    max_x = 13
                else:
                    if not midpoint.x + 6 <= world_size["x"]:
                        update_midpoint = True
                        min_x = world_size["x"] - 12
                        max_x = world_size["x"]
                    else:
                        min_x = midpoint.x - 6
                        max_x = midpoint.x + 6

                if not midpoint.y - 6 >= 1:
                    update_midpoint = True
                    min_y = 1
                    max_y = 13
                else:
                    if not midpoint.y + 6 <= world_size["y"]:
                        update_midpoint = True
                        min_y = world_size["y"] - 12
                        max_y = world_size["y"]
                    else:
                        min_y = midpoint.y - 6
                        max_y = midpoint.y + 6

                b_box_size = 50
                svg_scale_factor = 0.1
                if update_midpoint:
                    midpoint = LandUnit.objects.filter(x=min_x + 6, y=min_y + 6)[0]

            else:
                return HttpResponse("Don't know what to do with that zoom level... Sorry.")

            output["land"] = get_land(min_x, min_y, max_x, max_y)
            output["evopix"] = get_evopix(min_x, min_y, max_x, max_y, b_box_size, svg_scale_factor)
            output["midpoint"] = midpoint.land_id
            output = json.dumps(output)
            return HttpResponse(output)

        else:
            print("Failed post.")
            return HttpResponse("Fail")
    except:
        typ, value, tback = sys.exc_info()
        print("Error caught! %s" % traceback.print_tb(tback))
        return HttpResponse("Fail")


#-------------------------Sandbox-------------------------------#
def run():
    print()