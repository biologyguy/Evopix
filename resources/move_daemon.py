from resources.breed import *
from math import ceil
from django.http import HttpResponse
from evp.models import *
from world.models import *
from random import choice
import time


def _battle(enemy_id, evo_id):
        evo = Evopix.objects.filter(evo_id=evo_id).get()
        enemy = Evopix.objects.filter(evo_id=enemy_id).get()
        evo = Evopic(evo.evp)
        enemy = Evopic(enemy.evp)

        loser = choice((enemy_id, evo_id))
        return loser


def _look(self_min_max, direction):
    """
    This returns a dictionary of lists, containing land units that have fences, evopix, or lands_end units.
    Evopix list contains tuples -> (land_id, evo_id), and all others are land_id
    self_min_max is a dict, direction is in ["up", "down", "left", "right"]
    Only look to a depth of 1 in direction specified
    """
    min_x, min_y, max_x, max_y = [self_min_max["min_x"], self_min_max["min_y"], self_min_max["max_x"], self_min_max["max_y"]]
    visible_stuff = {"fences": {"top": [], "bottom": [], "left": [], "right": []}, "evopix": [], "lands_end": [], "land": []}

    # Get info on the visible land units
    if direction == "up":
        land = LandUnit.objects.filter(y__gte=(max_y + 1), x__gte=min_x, x__lte=max_x)
    elif direction == "down":
        land = LandUnit.objects.filter(y__lte=(min_y - 1), x__gte=min_x, x__lte=max_x)
    elif direction == "right":
        land = LandUnit.objects.filter(x__gte=(max_x + 1), y__gte=min_y, y__lte=max_y)
    else:  # left
        land = LandUnit.objects.filter(x__lte=(min_x - 1), y__gte=min_y, y__lte=max_y)

    for land_unit in land:
        visible_stuff["land"].append(land)

        if land_unit.evopic_id:
            visible_stuff["evopix"].append((land_unit.land_id, land_unit.evopic_id))

        if land_unit.t_fence_id:
            visible_stuff["fences"]["top"].append(land_unit.land_id)
        if land_unit.b_fence_id:
            visible_stuff["fences"]["bottom"].append(land_unit.land_id)
        if land_unit.l_fence_id:
            visible_stuff["fences"]["left"].append(land_unit.land_id)
        if land_unit.r_fence_id:
            visible_stuff["fences"]["right"].append(land_unit.land_id)

        if land_unit.type_id == 3:
            visible_stuff["lands_end"].append(land_unit.land_id)

    return visible_stuff


def _place_baby(parent_min_max, baby):
    baby_width = ceil(((baby.min_max_points["max_x"] - baby.min_max_points["min_x"]) * 0.1) / 50)
    baby_height = ceil(((baby.min_max_points["max_y"] - baby.min_max_points["min_y"]) * 0.1) / 50)
    baby_dimensions = {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}

    direction = choice(["up", "down", "left", "right"])
    if direction in ["up", "down"]:
        edge = choice(("right", "left"))
        if edge == "right":
            baby_dimensions["max_x"] = max_x
            baby_dimensions["min_x"] = max_x - int(baby_width - 1)
        else:  # "left"
            baby_dimensions["max_x"] = min_x + int(baby_width - 1)
            baby_dimensions["min_x"] = min_x

        if direction == "up":
            baby_dimensions["min_y"] = max_y + 1
            baby_dimensions["max_y"] = baby_dimensions["min_y"] + int(baby_height)

        else:  # down
            baby_dimensions["max_y"] = min_y - 1
            baby_dimensions["min_y"] = baby_dimensions["max_y"] - int(baby_height)

    else:  # direction in ["right", "left"]:
        edge = choice(("top", "bottom"))
        if edge == "top":
            baby_dimensions["max_y"] = max_y
            baby_dimensions["min_y"] = max_y - int(baby_height)
        else:  # "bottom"
            baby_dimensions["max_y"] = min_y + int(baby_height)
            baby_dimensions["min_y"] = min_y

        if direction == "right":
            baby_dimensions["min_x"] = max_x + 1
            baby_dimensions["max_x"] = baby_dimensions["min_x"] + int(baby_width - 1)

        else:  # left
            baby_dimensions["max_x"] = min_x - 1
            baby_dimensions["min_x"] = baby_dimensions["max_x"] - int(baby_width - 1)

    # Any fences in the way? There is still something wrong with this, because babys can be tossed over fences...
    # check for adjacent fences first
    if direction == "up":
        vis_stuff = _look(0, 1)
        for unit in vis_stuff["fences"]["top"]:
            if unit in adjacent_top(dimensions):
                return "Tried to breed, but found a fence"

    elif direction == "down":
        vis_stuff = _look(0, -1)
        for unit in vis_stuff["fences"]["bottom"]:
            if unit in adjacent_bottom(dimensions):
                return "Tried to breed, but found a fence"

    elif direction == "right":
        vis_stuff = _look(1, 0)
        for unit in vis_stuff["fences"]["right"]:
            if unit in adjacent_right(dimensions):
                return "Tried to breed, but found a fence"

    else:  # direction == 'left'
        vis_stuff = _look(-1, 0)
        for unit in vis_stuff["fences"]["left"]:
            if unit in adjacent_left(dimensions):
                return "Tried to breed, but found a fence"

    clear = True
    land_units = LandUnit.objects.filter(x__lte=baby_dimensions["max_x"], x__gte=baby_dimensions["min_x"],
                                        y__gte=baby_dimensions["min_y"], y__lte=baby_dimensions["max_y"])
    for land_unit in land_units:
        # top-right corner
        if land_unit.x == baby_dimensions["max_x"] and land_unit.y == baby_dimensions["max_y"]:
            if (land_unit.l_fence_id and baby_width > 1) or (land_unit.b_fence_id and baby_height > 1):
                clear = False
                break
        # bottom-right corner
        if land_unit.x == baby_dimensions["max_x"] and land_unit.y == baby_dimensions["min_y"]:
            if (land_unit.l_fence_id and baby_width > 1) or (land_unit.t_fence_id and baby_height > 1):
                clear = False
                break
        # bottom-left corner
        if land_unit.x == baby_dimensions["min_x"] and land_unit.y == baby_dimensions["min_y"]:
            if (land_unit.r_fence_id and baby_width > 1) or (land_unit.t_fence_id and baby_height > 1):
                clear = False
                break
        # top-left corner
        if land_unit.x == baby_dimensions["min_x"] and land_unit.y == baby_dimensions["max_y"]:
            if (land_unit.r_fence_id and baby_width > 1) or (land_unit.b_fence_id and baby_height > 1):
                clear = False
                break
        # bottom or top edge
        if land_unit.x not in [baby_dimensions["min_x"], baby_dimensions["max_x"]]\
                and (land_unit.y in [baby_dimensions["max_y"], baby_dimensions["min_y"]]):
            if land_unit.r_fence_id or land_unit.l_fence_id:
                clear = False
                break
        # left or right edge
        if land_unit.y not in [baby_dimensions["min_y"], baby_dimensions["max_y"]]\
                and (land_unit.x in [baby_dimensions["max_x"], baby_dimensions["min_x"]]):
            if land_unit.t_fence_id or land_unit.b_fence_id:
                clear = False
                break
        # anything internal
        if land_unit.x not in [baby_dimensions["min_x"], baby_dimensions["max_x"]]\
                and land_unit.y not in [baby_dimensions["min_y"], baby_dimensions["max_y"]]:
            if land_unit.t_fence_id or land_unit.b_fence_id or land_unit.l_fence_id or land_unit.r_fence_id:
                clear = False
                break

    if not clear:
        return "Tried to breed, but found a fence"

    # Any Evopix in the way?
    evos_in_the_way = []
    for land_unit in land_units:
        if land_unit.evopic_id:
            evos_in_the_way.append(land_unit.evopic_id)

    # If there are Evoix present, maybe fight to the death!
    if len(evos_in_the_way) > 0:
        if choice((True, False, False)):
            return "Tried to breed, but another evo was in the way"
        enemy_id = choice(evos_in_the_way)
        who_dies = _battle(enemy_id, evo_id)
        cleared_landunits = LandUnit.objects.filter(evopic_id=who_dies)
        cleared_landunits.update(evopic_id=None)
        dead_evo = Evopix.objects.filter(evo_id=who_dies)
        dead_evo.update(health=0)
        return "Killed evopic %s" % who_dies

    # Save the baby evopic and place it on the map
    else:
        baby.save(location="db", parents=(evo_id, mate.get().evo_id))
        land_units.update(evopic_id=baby.id)
        return "Got a new Evopic!"


def _move():
    living_evopix = Evopix.objects.filter(health__gt=0)
    evo_id = choice(living_evopix).evo_id
    land_units = LandUnit.objects.filter(evopic_id=evo_id)
    min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
    for land_unit in land_units:
        min_x = land_unit.x if land_unit.x < min_x else min_x
        min_y = land_unit.y if land_unit.y < min_y else min_y
        max_x = land_unit.x if land_unit.x > max_x else max_x
        max_y = land_unit.y if land_unit.y > max_y else max_y

    dimensions = {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}

    direction = choice(["up", "down", "left", "right"])
    # first check for flush fences
    if direction == "up":
        vis_stuff = _look(dimensions, "up")
        if len(vis_stuff["fences"]["bottom"]) != 0:
            return "fence"

    elif direction == "down":
        vis_stuff = _look(dimensions, "down")
        if len(vis_stuff["fences"]["top"]) != 0:
            return "fence"

    elif direction == "right":
        vis_stuff = _look(dimensions, "right")
        if len(vis_stuff["fences"]["left"]) != 0:
            return "fence"

    else:  # direction == 'left'
        vis_stuff = _look(dimensions, "left")
        if len(vis_stuff["fences"]["right"]) != 0:
            return "fence"

    # next check for side-on fences
    if direction in ["up", "down"]:
        vertical_fences = set(vis_stuff["fences"]["right"]).intersection(vis_stuff["fences"]["left"])
        if len(vertical_fences) > 0:
            return "fence"

    if direction in ["left", "right"]:
        horizontal_fences = set(vis_stuff["fences"]["top"]).intersection(vis_stuff["fences"]["bottom"])
        if len(horizontal_fences) > 0:
            return "fence"

    # bumped into an evopic, so try breeding
    if len(vis_stuff["evopix"]) > 0:
        mate_id = choice(vis_stuff["evopix"][1])
        mate = Evopix.objects.filter(evo_id=mate_id).get()
        evopic = Evopix.objects.filter(evo_id=evo_id).get()
        baby = breed(evopic.evp, mate.evp)
        outcome_of_breed_attempt = _place_baby(dimensions, baby)
        return outcome_of_breed_attempt

    else:
        if direction == "right":
            new_land = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
            old_land = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)
        elif direction == "left":
            new_land = LandUnit.objects.filter(y=min_y - 1, x__gte=min_x, x__lte=max_x)
            old_land = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)
        elif direction == "right":
            new_land = LandUnit.objects.filter(x=max_x + 1, y__gte=min_y, y__lte=max_y)
            old_land = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)
        else:  # left
            new_land = LandUnit.objects.filter(x=min_x - 1, y__gte=min_y, y__lte=max_y)
            old_land = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)

        new_land.update(evopic_id=evo_id)
        old_land.update(evopic_id=None)
        return "move"


def move(request):
    for _ in range(100):
        try_move = _move()
        print(try_move)
    return HttpResponse()


def run():
    for i in range(100000):
        _move()
        #time.sleep(0.25)
