#!/usr/bin/python3
try:
    from Evopic import *
except ImportError:
    from resources.Evopic import *

from random import random, choice, randint
from math import log, cos, sin, radians, factorial
import sys
from evp.models import *

# Mutation rates are the probability of an event happening per mutable character
mutation_rates = {"path_split": 0.0001, "point_split": 0.003, "del_point": 0.001, "point_move": 0.02,
                  "gradient_param": 0.01, "stop_split": 0.002, "del_stop": 0.001, "stop_params": 0.01,
                  "stroke_color": 0.01, "stroke_width": 0.01, "stroke_opacity": 0.01}

# 'Magnitudes' are coefficients that adjust mutational impact, determined empirically to 'feel' right
magnitudes = {"points": 0.03, "colors": 4, "opacity": 0.03, "max_stroke_width": 0.05, "stroke_width": 0.0005,
              "stop_params": 0.015, "gradient_params": 0.015}


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


def rand_move(coefficient):
# this f(x) moves nicely between 0 and infinity: 80% of returned values fall between 3% and 13% of the coefficient
    return coefficient * ((-2 * log(random(), 2)) ** 0.5)


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
    distance_changed = rand_move(magnitudes["points"] * path_size)
    direction_change = (random() * 360)
    change_x = sin(radians(direction_change)) * distance_changed
    change_y = cos(radians(direction_change)) * distance_changed

    for i in range(len(points)):
        points[i] = [points[i][0] + change_x, points[i][1] + change_y]
    return points


def move_in_range(cur_value, val_range, magnitude):
    dist_moved = rand_move(magnitude) * choice([1, -1])
    new_value = dist_moved + cur_value
    safety_check = 100
    while new_value < min(val_range) or new_value > max(val_range):
        if new_value < min(val_range):
            new_value = min(val_range) + abs(min(val_range) - new_value)

        elif new_value > max(val_range):
            new_value = max(val_range) - abs(max(val_range) - new_value)

        else:
            sys.exit("Error: %s" % new_value)

        if safety_check < 0:
            sys.exit("Popped safety valve on move_in_range()")
        safety_check -= 1

    return new_value


def mutate_color(color):  # Colour needs to be RGB hex values
    components = [int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)]
    which_component = randint(0, 2)
    components[which_component] = round(move_in_range(components[which_component], [0., 255.], magnitudes["colors"]))
    output = ""
    for i in range(3):
        output += hex(components[i])[2:].zfill(2)

    return output


def mutate(evopic):
    num_points = evopic.num_points()

    # insert new points
    # Insertion needs to interact with the database
    num_insertions = num_mutations(mutation_rates["point_split"], num_points)
    while num_insertions > 0:
        path_id, point_id = choice(evopic.point_locations())  # using 'point_locations()' ensures proper distribution
        evopic.point_split(path_id, point_id)
        num_insertions -= 1

    # delete points
    num_deletions = num_mutations(mutation_rates["del_point"], num_points)
    while num_deletions > 0:
        path_id, point_id = choice(evopic.point_locations())
        evopic.delete_point(path_id, point_id)
        num_deletions -= 1

    # Move points. Points can change by:
    # The point of one of the control handles move individually -> single: 70%
    # The point and its control handles move equally -> all: 25%
    # One of the control handles realigns with the other (smooths curve) -> equalize: 5%
    move_rates = {"single": 0.7, "all": 0.25, "equalize": 0.05}

    # Point and/or control handle(s)
    num_changes = num_mutations(mutation_rates["point_move"], num_points)
    while num_changes > 0:
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

        num_changes -= 1

    # Stroke parameters
    num_changes = num_mutations(mutation_rates["stroke_color"], len(evopic.paths))
    while num_changes > 0:
        path_id = choice(evopic.paths_order)
        path = evopic.paths[path_id]
        path.stroke[0] = mutate_color(path.stroke[0])
        evopic.paths[path_id] = path
        num_changes -= 1

    num_changes = num_mutations(mutation_rates["stroke_width"], len(evopic.paths))
    while num_changes > 0:
        path_id = choice(evopic.paths_order)
        path = evopic.paths[path_id]
        max_range = path.path_size() * magnitudes["max_stroke_width"]
        path.stroke[1] = move_in_range(path.stroke[1], [0., max_range], path.path_size() * magnitudes["stroke_width"])
        evopic.paths[path_id] = path
        num_changes -= 1

    num_changes = num_mutations(mutation_rates["stroke_opacity"], len(evopic.paths))
    while num_changes > 0:
        path_id = choice(evopic.paths_order)
        path = evopic.paths[path_id]
        path.stroke[2] = move_in_range(path.stroke[2], [0., 1.], magnitudes["opacity"])
        evopic.paths[path_id] = path
        num_changes -= 1

    # Gradient and stop parameters
    path_ids = []
    stop_locations = []
    for path_id in evopic.paths_order:
        if evopic.paths[path_id].type != "x":
            path_ids.append(path_id)
            for i in range(len(evopic.paths[path_id].stops)):
                stop_locations.append((path_id, i))

    num_changes = num_mutations(mutation_rates["gradient_param"], len(path_ids) * 2)  # Len(path_ids) is * 2 because they can be radial or linear
    while num_changes > 0:
        path_id = choice(path_ids)
        path = evopic.paths[path_id]
        grad_type = choice(["linear", "radial"])

        if grad_type == "linear":
            position = choice(range(len(path.linear)))
            path.linear[position] = move_in_range(path.linear[position], [0., 1.], magnitudes["gradient_params"])

        else:
            position = choice(range(len(path.radial)))
            path.radial[position] = move_in_range(path.radial[position], [0., 1.], magnitudes["gradient_params"])

        evopic.paths[path_id] = path
        num_changes -= 1

    num_changes = num_mutations(mutation_rates["stop_params"], len(stop_locations))
    while num_changes > 0:
        stop_loc = choice(stop_locations)
        stop = evopic.paths[stop_loc[0]].stops[stop_loc[1]]
        position = choice((0, 1, 2))
        if position == 0:
            stop["params"][0] = mutate_color(stop["params"][0])

        else:
            stop["params"][position] = move_in_range(stop["params"][position], [0., 1.], magnitudes["stop_params"])

        evopic.paths[stop_loc[0]].stops[stop_loc[1]] = stop
        num_changes -= 1

    # Stop splits, needs to interact with database
    blahh = 1


    # Stop deletions. Min # stops per path is 1.
    num_changes = num_mutations(mutation_rates["del_stop"], len(stop_locations) - len(path_ids))
    while num_changes > 0:
        deletable_stops = []
        for path_id in evopic.paths_order:
            if len(evopic.paths[path_id].stops) > 1:
                for i in range(len(evopic.paths[path_id].stops)):
                    deletable_stops.append((path_id, i))

        deleted_stop = choice(deletable_stops)
        del evopic.paths[deleted_stop[0]].stops[deleted_stop[1]]
        num_changes -= 1

    evopic.reconstruct_evp()
    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    import breed
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        bob = mutate(bob)
        baby = Evopic(breed.zero_evp(bob.evp))
        print("Hello")
    with open("../genomes/test.svg", "w") as ofile:
        ofile.write(baby.svg_out())
