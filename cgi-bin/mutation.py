#!/usr/bin/python3
from Evopic import Evopic
from similarity import find_path_area, find_path_length, line_length
from random import random
from math import log, pi, cos, sin, radians


def move_point(path_size, point):
    distance_changed = 0.05 * path_size  # This needs to take into account the size of the path
    direction_change = (random() * 360)
    change_x = sin(radians(direction_change)) * distance_changed
    change_y = cos(radians(direction_change)) * distance_changed
    return [change_x, change_y]


def mutate(evopic):
    mutation_rates = {"points": 0.025, "gradient": 0.01}

    for path_id in evopic.paths_order:
        path = evopic.paths[path_id]
        if path["type"] in ["r", "l"]:
            size = find_path_area(path) ** 0.5
            print(find_path_length(path), size * 4)

        else:
            size = find_path_length(path)
            print(size)

        for point in evopic.paths[path_id]["points"]:
            if random() < mutation_rates["points"]:
                print(move_point(size, point))
        #break

    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        bob = mutate(bob)
        #print(bob.svg_out())

    #with open("../genomes/test.svg", "w") as ofile:
    #    ofile.write(bob.svg_out())

