#!/usr/bin/python3
from Evopic import *
from random import random, choice
from math import log, pi, cos, sin, radians, factorial, exp


def choose(n, k):  # n = sample size. k = number chosen. ie n choose k
    if k == 0 or k == n:
        return 1

    elif k == 1 or k == n - 1:
        return n

    else:
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

    return [point[0] + change_x, point[1] + change_y]


def mutate(evopic):
    mutation_rates = {"path_split": (1./10000.), "insert_point": 0.05, "del_point": 0.05, "point_move": 0.025, "gradient": 0.01}
    magnitudes = {"points": 0.05}
    num_points = evopic.num_points()

    # insert new points
    for i in range(num_mutations(mutation_rates["insert_point"], num_points)):
        if i == 0:
            continue
        #print(sample(evopic.paths.items(), 1))

    for path_id in evopic.paths_order:
        path = evopic.paths[path_id]
        size = path.path_size()
        #print(size)

        for point_id in path.points_order:
            point = path.points[point_id]
            if random() < mutation_rates["point_move"]:
                x = 1
                #print(move_point(size, point[1]))
        #break

    #delete points
    num_deletions = num_mutations(mutation_rates["del_point"], num_points)
    while num_deletions > 0:
        path_id, point_id = choice(evopic.point_locations())
        evopic.delete_point(path_id, point_id)
        num_deletions -= 1
        print(path_id, point_id)

    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        bob = mutate(bob)
        #print(bob.svg_out())

    with open("../genomes/test.svg", "w") as ofile:
        ofile.write(bob.svg_out())

