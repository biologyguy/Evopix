from resources.breed import *
from math import ceil
from django.http import HttpResponse
from django.db.models import Q
from evp.models import *
from world.models import *
from random import choice, random
import time
import pdb


class Look():
    """
    Class for peeking around at nearby land units to see if they have fences, evopix, or lands_end units.
    Evopix list contains tuples -> (land_id, evo_id), and all others are land_id
    self_min_max is a dict, direction is in ["up", "down", "left", "right"]
    """
    def __init__(self, self_min_max, direction):
        self.min_x, self.min_y, self.max_x, self.max_y = [self_min_max["min_x"], self_min_max["min_y"], self_min_max["max_x"], self_min_max["max_y"]]
        self.direction = direction
        self.fences = {"top": [], "bottom": [], "left": [], "right": []}
        self.evopix = []
        self.lands_end = []
        self.land = []

        self.visible_stuff()

    def visible_stuff(self):
        visible_stuff = {"fences": {"top": [], "bottom": [], "left": [], "right": []}, "evopix": [], "lands_end": [], "land": []}
        # Get info on the visible land units
        if self.direction == "up":
            land = LandUnit.objects.filter(y=(self.max_y + 1), x__gte=self.min_x, x__lte=self.max_x)
        elif self.direction == "down":
            land = LandUnit.objects.filter(y=(self.min_y - 1), x__gte=self.min_x, x__lte=self.max_x)
        elif self.direction == "right":
            land = LandUnit.objects.filter(x=(self.max_x + 1), y__gte=self.min_y, y__lte=self.max_y)
        elif self.direction == "left":
            land = LandUnit.objects.filter(x=(self.min_x - 1), y__gte=self.min_y, y__lte=self.max_y)
        else:
            sys.exit("Error: '%s' is not a valid direction" % self.direction)

        for land_unit in land:
            visible_stuff["land"].append(land_unit)

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

        self.fences = visible_stuff["fences"]
        self.evopix = visible_stuff["evopix"]
        self.lands_end = visible_stuff["lands_end"]
        self.land = visible_stuff["land"]

        return

    def blocking_fence(self):
        # first check for flush fences
        if self.direction == "up":
            if len(self.fences["bottom"]) != 0:
                return True

        elif self.direction == "down":
            if len(self.fences["top"]) != 0:
                return True

        elif self.direction == "right":
            if len(self.fences["left"]) != 0:
                return True

        elif self.direction == "left":
            if len(self.fences["right"]) != 0:
                return True

        # next check for side-on fences
        if self.direction in ["up", "down"]:
            vertical_fences = set(self.fences["right"]).intersection(self.fences["left"])
            if len(vertical_fences) > 0:
                return True

        if self.direction in ["left", "right"]:
            horizontal_fences = set(self.fences["top"]).intersection(self.fences["bottom"])
            if len(horizontal_fences) > 0:
                return True

        # No blocking fences!!
        return False

    def step_deeper(self):
        if self.direction == "up":
            self.min_y += 1
            self.max_y += 1
        if self.direction == "down":
            self.min_y -= 1
            self.max_y -= 1
        if self.direction == "right":
            self.min_x += 1
            self.max_x += 1
        if self.direction == "left":
            self.min_x -= 1
            self.max_x -= 1

        self.visible_stuff()
        return


def _battle(enemy_id, evo_id):
        evo = Evopix.objects.filter(evo_id=evo_id).get()
        enemy = Evopix.objects.filter(evo_id=enemy_id).get()
        evo = Evopic(evo.evp)
        enemy = Evopic(enemy.evp)

        advantage_factors = {"biggest": 1.5, "oldest": 1.5, "most_points": 1.5}

        evo_score = 1.
        enemy_score = 1.
        # Largest evopic has an advantage
        evo_size = evo.size()
        enemy_size = enemy.size()
        if evo_size > enemy_size:
            evo_score *= advantage_factors["biggest"]
        elif evo_size < enemy_size:
            enemy_score *= advantage_factors["biggest"]

        # Older (smaller id) points have an advantage
        if evo.ave_points_age() > enemy.ave_points_age():
            evo_score *= advantage_factors["oldest"]
        elif evo.ave_points_age() < enemy.ave_points_age():
            enemy_score *= advantage_factors["oldest"]

        # More points has an advantage
        if evo.num_points() > enemy.num_points():
            evo_score *= advantage_factors["most_points"]
        elif evo.num_points() < enemy.num_points():
            enemy_score *= advantage_factors["most_points"]

        # Select the winner from weighted probability based on score
        if evo_score / (evo_score + enemy_score) < random():
            loser = enemy_id
        else:
            loser = evo_id

        return loser


def _get_land_units(dimensions):  # dimensions -> {"min_x", "max_x", "min_y", "max_y"}
    land_units = LandUnit.objects.filter(x__gte=dimensions["min_x"],
                                         x__lte=dimensions["max_x"],
                                         y__gte=dimensions["min_y"],
                                         y__lte=dimensions["max_y"])
    return land_units


def _place_baby(parent1, parent2, baby):
    baby_width = ceil(((baby.min_max_points["max_x"] - baby.min_max_points["min_x"]) * 0.1) / 50)
    baby_height = ceil(((baby.min_max_points["max_y"] - baby.min_max_points["min_y"]) * 0.1) / 50)
    baby_dimensions = {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}

    # start by overlaying the parent, starting at a random corner (in case the baby is bigger or smaller)
    parent_dimensions = parent1.world_dimensions
    d = parent_dimensions
    corner = choice(["tl", "tr", "bl", "br"])
    if corner == "tl":
        baby_dimensions["min_x"] = d["min_x"]
        baby_dimensions["max_x"] = d["min_x"] + (baby_width - 1)
        baby_dimensions["min_y"] = d["max_y"] - (baby_height - 1)
        baby_dimensions["max_y"] = d["max_y"]

    elif corner == "tr":
        baby_dimensions["min_x"] = d["max_x"] - (baby_width - 1)
        baby_dimensions["max_x"] = d["max_x"]
        baby_dimensions["min_y"] = d["max_y"] - (baby_height - 1)
        baby_dimensions["max_y"] = d["max_y"]

    elif corner == "bl":
        baby_dimensions["min_x"] = d["min_x"]
        baby_dimensions["max_x"] = d["min_x"] + (baby_width - 1)
        baby_dimensions["min_y"] = d["min_y"]
        baby_dimensions["max_y"] = d["min_y"] + (baby_height - 1)

    else:  # "corner == br"
        baby_dimensions["min_x"] = d["max_x"] - (baby_width - 1)
        baby_dimensions["max_x"] = d["max_x"]
        baby_dimensions["min_y"] = d["min_y"]
        baby_dimensions["max_y"] = d["min_y"] + (baby_height - 1)

    # Ensure that the baby isn't sitting on top of any fences after overlay (in case baby is bigger than parent)
    land_units = _get_land_units(baby_dimensions)
    fences = {"t": [], "b": [], "r": [], "l": []}
    for l in land_units:
        fences["t"].append(l.t_fence_id) if l.t_fence_id else False
        fences["b"].append(l.b_fence_id) if l.b_fence_id else False
        fences["r"].append(l.r_fence_id) if l.r_fence_id else False
        fences["l"].append(l.l_fence_id) if l.l_fence_id else False

    horizontal_fences = set(fences["t"]).intersection(fences["b"])
    if len(horizontal_fences) > 0:
        return "fence"

    vertical_fences = set(fences["r"]).intersection(fences["l"])
    if len(vertical_fences) > 0:
        return "fence"

    # pick a direction, shift baby to edge, and see if the way is clear
    direction = choice(["up", "down", "left", "right"])
    if direction == "left":
        baby_dimensions["min_x"] = parent_dimensions["min_x"]
        baby_dimensions["max_x"] = baby_dimensions["min_x"] + baby_width - 1
    elif direction == "right":
        baby_dimensions["max_x"] = parent_dimensions["max_x"]
        baby_dimensions["min_x"] = baby_dimensions["max_x"] - baby_width + 1
    elif direction == "down":
        baby_dimensions["min_y"] = parent_dimensions["min_y"]
        baby_dimensions["max_y"] = baby_dimensions["min_y"] + baby_height - 1
    elif direction == "up":
        baby_dimensions["max_y"] = parent_dimensions["max_y"]
        baby_dimensions["min_y"] = baby_dimensions["max_y"] - baby_height + 1
    else:
        sys.exit("Error: no direction is detected")
    dist_moved = baby_width if direction in ["right", "left"] else baby_height

    look = Look(baby_dimensions, direction)
    evos_in_the_way = []
    final_position = []
    for i in range(dist_moved):
        if look.blocking_fence():
            return "fence"
        if len(look.lands_end) > 0:
            return "Edge of the world"
        evos_in_the_way += look.evopix
        final_position += look.land
        if i + 1 < dist_moved:
            look.step_deeper()

    # If there are Evoix present, maybe fight to the death!
    if len(evos_in_the_way) > 0:
        if choice((True, False, False)):  # Arbitrarily setting the likelihood of fight
            return "evo in the way"
        # !!!!! Remove this call when there are more than a handful of evos in the world
        if len(Evopix.objects.filter(health__gt=0)) < 5:
            return "Too few Evos alive to allow fighting..."
        enemy_id = choice(evos_in_the_way)[1]  # The first index is land_id

        loser = Evopic()  # No need to actually fill the object in the constructor, just set the id after instantiate
        loser.id = _battle(enemy_id, parent1.id)
        loser.death()
        return "Killed evopic %s" % loser.id

    # Save the baby evopic and place it on the map
    else:
        look.step_deeper()  # just bump the look min_max one more step to finish the move
        land = LandUnit.objects.filter(y__gte=look.min_y, y__lte=look.max_y, x__gte=look.min_x, x__lte=look.max_x)
        baby.save(location="db", parents=(parent1.id, parent2.id))
        land.update(evopic_id=baby.id)
        return "Got a new Evopic!"


def _move():
    living_evopix = Evopix.objects.filter(health__gt=0)
    evo_id = choice(living_evopix).evo_id
    dimensions = Evopic.world_xy(evo_id)

    direction = choice(["up", "down", "left", "right"])
    look = Look(dimensions, direction)
    if look.blocking_fence():
        return "fence"

    if len(look.lands_end) != 0:
        return "Edge of the world"

    if len(look.evopix) > 0:  # bumped into an evopic, so try breeding
        mate_id = choice(look.evopix)  # Note: the evopix are tuples -> (land_id, evopic_id)
        # mate = Evopix.objects.filter(evo_id=mate_id[1]).get()
        mate = Evopic(evo_id=mate_id[1])
        # evopic = Evopix.objects.filter(evo_id=evo_id).get()
        evopic = Evopic(evo_id=evo_id)
        baby = breed(evopic, mate)
        outcome_of_breed_attempt = _place_baby(evopic, mate, baby)
        return outcome_of_breed_attempt

    else:
        d = dimensions
        min_x, min_y, max_x, max_y = [d["min_x"], d["min_y"], d["max_x"], d["max_y"]]
        if direction == "up":
            new_land = LandUnit.objects.filter(y=max_y + 1, x__gte=min_x, x__lte=max_x)
            old_land = LandUnit.objects.filter(y=min_y, x__gte=min_x, x__lte=max_x)
        elif direction == "down":
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


import sys, select

def run():
    # This will break if the Enter key if pressed
    i = 0
    while True:
        print(_move())
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = input()
            break
        i += 1