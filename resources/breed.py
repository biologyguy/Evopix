#! /usr/bin/python
from resources.Evo import *
from evp.models import *
from world.models import *
from random import choice
from resources import mutation


def breed(evp1, evp2):
    """Notes:-The original evp file (i.e., not zeroed) needs to be used for breeding.
             -moderate to extreme values in offset and radius totally break the fill of a gradient in some browsers
             -Pass in parents as evopic objects.
    """
    parent = Evopic(choice([evp1, evp2]))
    baby = mutation.mutate(parent)
    return baby


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        print(bob.paths[1].points_order)
    with open("../genomes/sue.evp", "r") as infile:
        sue = Evopic(infile.read())
    print("HELLO!")