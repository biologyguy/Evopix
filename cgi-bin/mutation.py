#!/usr/bin/python3
from Evopic import *
from random import random, choice, randint
from math import log, pi, cos, sin, radians, factorial, exp
import sys


def choose(n, k):  # n = sample size. k = number chosen. ie n choose k
    if k == 0 or k == n:
        return 1

    elif k == 1 or k == n - 1:
        return n

    else:
        return factorial(n) / (factorial(k) * factorial(n - k))


def pick(option_dict):
    check_options = 0.
    for option in option_dict:
        check_options += option_dict[option]

    if check_options != 1.0:
        sys.exit("Error: %s, pick(). Options in option_dict must sum to 1")

    rand_num = random()
    for option in option_dict:
        if rand_num < option_dict[option]:
            return option
        else:
            rand_num -= option_dict[option]


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


def move_points(path_size, points):  # get path_size with path_size() function, and points is a list
    distance_changed = 0.05 * path_size  # Make a fancy equation that accounts for path size and levels off somewhere between 0.0 and 0.05
    direction_change = (random() * 360)
    change_x = sin(radians(direction_change)) * distance_changed
    change_y = cos(radians(direction_change)) * distance_changed

    for i in range(len(points)):
        points[i] = [points[i][0] + change_x, points[i][1] + change_y]
    return points


def mutate(evopic):
    mutation_rates = {"path_split": 0.0001, "insert_point": 0.005, "del_point": 0.005, "point_move": 0.025, "gradient": 0.01}
    magnitudes = {"points": 0.05}
    num_points = evopic.num_points()

    # insert new points
    # This needs to interact with the database
    num_deletions = num_mutations(mutation_rates["del_point"], num_points)
    print("Insertions")
    while num_deletions > 0:
        path_id, point_id = choice(evopic.point_locations())
        evopic.insert_point(path_id, point_id)
        num_deletions -= 1
        print(path_id, point_id)

    # delete points
    num_deletions = num_mutations(mutation_rates["del_point"], num_points)
    print("Deletions")
    while num_deletions > 0:
        path_id, point_id = choice(evopic.point_locations())
        evopic.delete_point(path_id, point_id)
        num_deletions -= 1
        print(path_id, point_id)

    # Move points. Points can change by:
    # The point of one of the control handles move individually -> single: 70%
    # The point and its control handles move equally -> all: 25%
    # One of the control handles realigns with the other (smooths curve) -> equalize: 5%
    move_rates = {"single": 0.7, "all": 0.25, "equalize": 0.05}

    print("Movements")
    num_movements = num_mutations(mutation_rates["point_move"], num_points)

    # Point and/or control handle(s)
    while num_movements > 0:
        path_id, point_id = choice(evopic.point_locations())
        path = evopic.paths[path_id]
        point = path.points[point_id]
        move_type = pick(move_rates)

        if move_type == "single":
            which_point = randint(0, 2)
            evopic.paths[path_id].points[point_id][which_point] = move_points(path.path_size(), [point[which_point]])[0]

        if move_type == "all":
            evopic.paths[path_id].points[point_id] = move_points(path.path_size(), point)

        if move_type == "equalize":
            # Distance between the moving control handle and path point stays the same, but the location of the moving
            # handle pivots around the path point until it is on the line created by the path point and static control
            # handle. This effectively smooths the Bezier curve.
            static_handle = choice([0, 2])
            move_handle = 2 if static_handle == 0 else 0

            move_length = LineSeg(point[move_handle], point[1]).length()
            static_line = LineSeg(point[static_handle], point[1])

            # Find the new point by calculating the two intercepts between the Line and a circle of radius 'move_length'
            # and then determining which of the two is furthest from 'static_handle'.
            x1 = point[1][0] + move_length / (1 + (static_line.slope() ** 2)) ** 0.5
            y1 = x1 * static_line.slope() + static_line.intercept()
            new_point1 = [x1, y1]

            x2 = point[1][0] - move_length / (1 + (static_line.slope() ** 2)) ** 0.5
            y2 = x2 * static_line.slope() + static_line.intercept()
            new_point2 = [x2, y2]

            new_length1 = LineSeg(point[static_handle], new_point1).length()
            new_length2 = LineSeg(point[static_handle], new_point2).length()

            final_new_point = new_point1 if new_length1 > new_length2 else new_point2

            evopic.paths[path_id].points[point_id][move_handle] = final_new_point

        num_movements -= 1

    evopic.reconstruct_evp()
    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    import breed
    with open("../genomes/test.evp", "r") as infile:
        bob = Evopic(infile.read())
        bob = mutate(bob)
        #print(breed.zero_evp(bob.evp))

    with open("../genomes/test.svg", "w") as ofile:
        ofile.write(bob.svg_out())

