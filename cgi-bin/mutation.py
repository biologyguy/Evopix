#!/usr/bin/python3
from Evopic import *
from random import random
from math import log, pi, cos, sin, radians, factorial, exp


def choose(n, k):  # n = sample size. k = number chosen. ie n choose k
    return factorial(n)/(factorial(k) * factorial(n - k))


def num_mutations(mu, num_items):  # mu = probability of success per item
    mutations = 0
    test_value = random()
    prob_sum = 0.

    for k in range(num_items):
        prob_sum += choose(num_items, k) * (mu ** k) * ((1. - mu) ** (num_items - k))
        if prob_sum < test_value:
            mutations += 1
            continue
        else:
            break

    return mutations


def move_point(path_size, point):
    distance_changed = 0.05 * path_size  # This needs to take into account the size of the path
    direction_change = (random() * 360)
    change_x = sin(radians(direction_change)) * distance_changed
    change_y = cos(radians(direction_change)) * distance_changed
    return [change_x, change_y]


def mutate(evopic):
    mutation_rates = {"path_split": (1./10000.), "points": 0.025, "gradient": 0.01}
    magnitudes = {"points": 0.05}
    num_points = evopic.num_points()

    for path_id in evopic.paths_order:
        path = evopic.paths[path_id]
        if path.type in ["r", "l"]:
            size = path.find_area() ** 0.5
            print(path.find_perimeter(), size * 4)

        else:
            size = path.find_perimeter()
            print(size)

        for point_id in path.points_order:
            point = path.points[point_id]
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

