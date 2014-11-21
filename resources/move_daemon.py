from resources.breed import *
from math import ceil
from django.http import HttpResponse
from evp.models import *
from world.models import *
from random import choice
import time


def _move():
    def battle(enemy_id, evo_id):
        evo = Evopix.objects.filter(evo_id=evo_id).get()
        enemy = Evopix.objects.filter(evo_id=enemy_id).get()
        evo = Evopic(evo.evp)
        enemy = Evopic(enemy.evp)

        print(evo.paths_order)
        sys.exit()
        loser = choice((enemy_id, evo_id))
        return loser

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

    dimensions = {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}

    # This next super-block of functions return the location of edges (i.e., where fences live) surrounding an evopic
    def adjacent_top(min_max):
        output = []
        for x in range(min_max["min_x"], min_max["max_x"] + 1):
            output.append((x, min_max["max_y"]))
        return output

    def adjacent_bottom(min_max):
        output = []
        for x in range(min_max["min_x"], min_max["max_x"] + 1):
            output.append((x, min_max["min_y"]))
        return output

    def adjacent_right(min_max):
        output = []
        for y in range(min_max["min_y"], min_max["max_y"] + 1):
            output.append((min_max["max_x"], y))
        return output

    def adjacent_left(min_max):
        output = []
        for y in range(min_max["min_y"], min_max["max_y"] + 1):
            output.append((min_max["min_x"], y))
        return output

    def edge_top(min_max):
        output = []
        for i in range(min_max["max_x"] - min_max["min_x"]):
            output.append((min_max["min_x"] + i, min_max["max_y"] + 1))
        return output

    def edge_bottom(min_max):
        output = []
        for i in range(min_max["max_x"] - min_max["min_x"]):
            output.append((min_max["min_x"] + i, min_max["min_y"] - 1))
        return output

    def edge_right(min_max):
        output = []
        for i in range(min_max["max_y"] - min_max["min_y"]):
            output.append((min_max["max_x"] + 1, min_max["min_y"] + i))
        return output

    def edge_left(min_max):
        output = []
        for i in range(min_max["max_y"] - min_max["min_y"]):
            output.append((min_max["min_x"] - 1, min_max["min_y"] + i))
        return output

    direction = choice(["up", "down", "left", "right"])

    if direction == "up":
        neighborhood = look(0, 1)
        for unit in neighborhood["fences"]["top"]:
            if unit in adjacent_top(dimensions):
                return "Fences above"
        for unit in neighborhood["fences"]["right"]:
            if unit in edge_top(dimensions):
                return "Fence in adjacent cells above"

        new_landunits = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
        old_landunits = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)

    elif direction == "down":
        neighborhood = look(0, -1)
        for unit in neighborhood["fences"]["bottom"]:
            if unit in adjacent_bottom(dimensions):
                return "Fences below"
        for unit in neighborhood["fences"]["right"]:
            if unit in edge_bottom(dimensions):
                return "Fence in adjacent cells below"

        new_landunits = LandUnit.objects.filter(y=min_y - 1, x__gte=min_x, x__lte=max_x)
        old_landunits = LandUnit.objects.filter(y=max_y, x__gte=min_x, x__lte=max_x)

    elif direction == "right":
        neighborhood = look(1, 0)
        for unit in neighborhood["fences"]["right"]:
            if unit in adjacent_right(dimensions):
                return "Fence to right"
        for unit in neighborhood["fences"]["top"]:
            if unit in edge_right(dimensions):
                return "Fence in adjacent cells to right"

        new_landunits = LandUnit.objects.filter(x=max_x + 1, y__gte=min_y, y__lte=max_y)
        old_landunits = LandUnit.objects.filter(x=min_x, y__gte=min_y, y__lte=max_y)

    else:  # direction == 'left'
        neighborhood = look(-1, 0)
        for unit in neighborhood["fences"]["left"]:
            if unit in adjacent_left(dimensions):
                return "Fence to left"
        for unit in neighborhood["fences"]["top"]:
            if unit in edge_left(dimensions):
                return "Fence in adjacent cells to left"

        new_landunits = LandUnit.objects.filter(x=min_x - 1, y__gte=min_y, y__lte=max_y)
        old_landunits = LandUnit.objects.filter(x=max_x, y__gte=min_y, y__lte=max_y)

    if len(neighborhood["evopix"]) > 0:
        evopic = Evopix.objects.filter(evo_id=evo_id).get().evp
        mate = Evopix.objects.filter(evo_id=choice(neighborhood["evopix"])[0])
        baby = breed(evopic, mate.get().evp)
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
        landunits = LandUnit.objects.filter(x__lte=baby_dimensions["max_x"], x__gte=baby_dimensions["min_x"],
                                            y__gte=baby_dimensions["min_y"], y__lte=baby_dimensions["max_y"])
        clear = True
        for landunit in landunits:
            if landunit.x == baby_dimensions["max_x"] and landunit.y == baby_dimensions["max_y"]:
                if landunit.l_fence_id or landunit.b_fence_id:
                    clear = False
                    break
            elif landunit.x == baby_dimensions["max_x"] and landunit.y == baby_dimensions["min_y"]:
                if landunit.l_fence_id or landunit.t_fence_id:
                    clear = False
                    break
            elif landunit.x == baby_dimensions["min_x"] and landunit.y == baby_dimensions["min_y"]:
                if landunit.r_fence_id or landunit.t_fence_id:
                    clear = False
                    break
            elif landunit.x == baby_dimensions["min_x"] and landunit.y == baby_dimensions["max_y"]:
                if landunit.r_fence_id or landunit.b_fence_id:
                    clear = False
                    break
            elif landunit.x == baby_dimensions["max_y"] or landunit.x == baby_dimensions["min_y"]:
                if landunit.r_fence_id or landunit.l_fence_id:
                    clear = False
                    break
            elif landunit.x == baby_dimensions["max_x"] or landunit.x == baby_dimensions["min_x"]:
                if landunit.t_fence_id or landunit.b_fence_id:
                    clear = False
                    break
            else:
                if landunit.t_fence_id or landunit.b_fence_id or landunit.l_fence_id or landunit.r_fence_id:
                    clear = False
                    break

        if not clear:
            return "Tried to breed, but found a fence"

        # Any Evopix in the way?
        evos_in_the_way = []
        for landunit in landunits:
            if landunit.evopic_id:
                evos_in_the_way.append(landunit.evopic_id)

        # If there are Evoix present, maybe fight to the death!
        if len(evos_in_the_way) > 0:
            if choice((True, False, False)):
                return "Tried to breed, but another evo was in the way"
            enemy_id = choice(evos_in_the_way)
            who_dies = battle(enemy_id, evo_id)
            cleared_landunits = LandUnit.objects.filter(evopic_id=who_dies)
            cleared_landunits.update(evopic_id=None)
            dead_evo = Evopix.objects.filter(evo_id=who_dies)
            dead_evo.update(health=0)
            return "Killed evopic %s" % who_dies

        # Save the baby evopic and place it on the map
        else:
            baby.save(location="db", parents=(evo_id, mate.get().evo_id))
            landunits.update(evopic_id=baby.id)
            return "Got a new Evopic!"

    else:
        new_landunits.update(evopic_id=evo_id)
        old_landunits.update(evopic_id=None)
        return "Evo %s moving %s" % (evo_id, direction)


def move(request):
    for _ in range(100):
        try_move = _move()
        print(try_move)
    return HttpResponse()


def run():
    for i in range(100000):
        _move()
        #time.sleep(0.25)
