#! /usr/bin/python
try:
    from Evo import *
except ImportError:
    from resources.Evo import *


def breed(evp1, evp2):
    """Notes:-The original evp file (i.e., not zeroed) needs to be used for breeding. Store the zeroed evp for printing.
             -moderate to extreme values in offset and radius totally break the fill of a gradient in some browsers
             -Pass in parents as evopic objects.
    """
    return "A couple of Evopics just made a baby.\n"


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        print(bob.paths[1].points_order)
    with open("../genomes/sue.evp", "r") as infile:
        sue = Evopic(infile.read())
    print("HELLO!")