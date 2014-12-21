#!/usr/bin/env python3
from resources.Evo import *
from evp.models import *
from world.models import *
from random import choice
from resources import mutation
from numpy import random

def breed(evopic1, evopic2):
    """Notes:-The original evp file (i.e., not zeroed) needs to be used for breeding.
             -moderate to extreme values in offset and radius totally break the fill of a gradient in some browsers
             -Pass in parents as evopic objects.
    """
    parent = choice([evopic1, evopic2])
    baby = mutation.mutate(parent)
    return baby


#-------------------------Sandbox-------------------------------#
def run():
    def set_parent_weight():
        new_weight = random.normal(loc=0.5, scale=0.15)
        new_weight = 1.0 if new_weight > 1.0 else new_weight
        new_weight = 0.0 if new_weight < 0.0 else new_weight
        return new_weight

    def recombination():
        num_points_before_change = round(random.normal(loc=25, scale=10))
        num_points_before_change = 2 if num_points_before_change < 2 else num_points_before_change
        return {"num_points": num_points_before_change, "rel_weight": set_parent_weight()}

    bob = Evopix.objects.filter(evo_id=1).get()
    bob = Evopic(bob.evp)
    sue = Evopix.objects.filter(evo_id=1903).get()
    sue = Evopic(sue.evp)

    baby = Evopic()

    # Start by building paths_order.
    path_ids = []
    bob_index = 0
    sue_index = 0
    while bob_index < len(bob.paths_order) and sue_index < len(sue.paths_order):
        if bob.paths_order[bob_index] not in sue.paths_order:
            if random.random() > 0.5:  # Coin flip to keep if path is unique to Bob
                path_ids.append(bob.paths_order[bob_index])
            bob_index += 1
        elif sue.paths_order[sue_index] not in bob.paths_order:
            if random.random() > 0.5:  # Coin flip to keep if path is unique to Sue
                path_ids.append(sue.paths_order[sue_index])
            sue_index += 1
        else:
            path_ids.append(bob.paths_order[bob_index])
            path_ids.append(sue.paths_order[sue_index])
            bob_index += 1
            sue_index += 1
    # Only ever keep one instance of a path index, randomly choosing one or the other (in the event that there are
    # descrepencies in index position).
    while len(path_ids) > 0:
        remaining = path_ids[1:]
        if path_ids[0] not in remaining:
            baby.paths_order.append(path_ids[0])
            path_ids = path_ids[1:]
        else:
            if random.random() > 0.5:
                baby.paths_order.append(path_ids[0])
                duplicate_index = remaining.index(path_ids[0])
                remaining = remaining[:duplicate_index] + remaining[duplicate_index + 1:]
                path_ids = remaining
            else:
                path_ids = path_ids[1:]

    print(baby.paths_order)