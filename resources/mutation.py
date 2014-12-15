#!/usr/bin/python3

from resources.Evo import *
from resources.LineSeg import *
from evp.models import *
from random import random, choice, randint
from math import cos, sin, radians, factorial
from copy import copy
import sys
from scipy.stats import gamma

# Mutation rates are the probability of an event happening per mutable character
mutation_rates = {"path_split": 0.0001, "point_split": 0.01, "del_point": 0.001, "point_move": 0.03,
                  "gradient_param": 0.01, "stop_split": 0.002, "del_stop": 0.001, "stop_params": 0.03,
                  "stroke_color": 0.05, "stroke_width": 0.01, "stroke_opacity": 0.01}

# test values for mutation rates.
#mutation_rates = {"path_split": 0.1, "point_split": 0.3, "del_point": 0.1, "point_move": 0.2,
#                  "gradient_param": 0.1, "stop_split": 0.2, "del_stop": 0.1, "stop_params": 0.5,
#                  "stroke_color": 0.1, "stroke_width": 0.1, "stroke_opacity": 0.1}

# 'Magnitudes' are coefficients that adjust mutational impact, determined empirically to 'feel' right
magnitudes = {"points": 0.03, "colors": 5, "opacity": 0.03, "max_stroke_width": 0.05, "stroke_width": 0.0005,
              "stop_params": 0.015, "gradient_params": 0.015}


# choose() will break when k gets too big. Need to figure something else out.
def choose(n, k):  # n = sample size. k = number chosen. ie n choose k
    if k == 0 or k == n:
        return 1

    elif k == 1 or k == n - 1:
        return n

    else:
        return factorial(n) / (factorial(k) * factorial(n - k))


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
# Using the SciPy package here to draw from a gamma distribution. Should try to implement this directly at some point.
    distribution = gamma(1.15, loc=0.01, scale=0.4)  # values determined empirically
    rand_draw = distribution.rvs()
    output = rand_draw * coefficient
    return output


def move_points(path_size, points):  # get path_size with path_size() function, and points is a list
    distance_changed = rand_move(magnitudes["points"] * path_size)
    direction_change = (random() * 360)
    change_x = sin(radians(direction_change)) * distance_changed
    change_y = cos(radians(direction_change)) * distance_changed

    for point_index in range(len(points)):
        points[point_index] = [points[point_index][0] + change_x, points[point_index][1] + change_y]
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
            import traceback
            sys.exit("Popped safety valve on move_in_range()\n%s\n%s, %s, %s" % (traceback.print_stack(), cur_value,
                                                                                 val_range, magnitude))
        safety_check -= 1

    return new_value


def mutate_color(color):  # Colour needs to be RGB hex values
    components = [int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)]
    which_component = randint(0, 2)
    components[which_component] = round(move_in_range(components[which_component], [0., 255.], magnitudes["colors"]))
    output = ""
    for comp_index in range(3):
        output += hex(components[comp_index])[2:].zfill(2)

    return output


def mutate(evopic):
    num_points = evopic.num_points()

    # Insert new points. This duplicates a point wholesale, which causes the path to kink up. Maybe this behavior
    # will need to be changed, but for now let's go with it to see how things unfold.
    num_changes = num_mutations(mutation_rates["point_split"], num_points)
    split_ids = []
    while num_changes > 0:
        path_id, point_id = choice(evopic.point_locations())  # using 'point_locations()' ensures proper distribution
        if point_id < 0 or point_id in split_ids:
            # in the unlikely event that a new point is selected for a split, or a point that has already been
            # split, try again.
            continue
        split_ids.append(point_id)
        path = evopic.paths[path_id]
        new_point = copy(path.points[point_id])
        order_index = path.points_order.index(point_id)
        new_position = choice([order_index, order_index + 1])

        if new_position == order_index:
            new_point[2] = new_point[1]
            path.points[point_id][0] = path.points[point_id][1]

        else:
            new_point[0] = new_point[1]
            path.points[point_id][2] = path.points[point_id][1]

        point_id *= -1
        path.points[point_id] = new_point
        path.points_order.insert(new_position, point_id)
        evopic.point_locations().append((path_id, point_id))

        num_changes -= 1

    # delete points
    num_changes = num_mutations(mutation_rates["del_point"], num_points)
    while num_changes > 0:
        path_id, point_id = choice(evopic.point_locations())
        evopic.delete_point(path_id, point_id)
        num_changes -= 1

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
    stop_locations = evopic.stop_locations()
    closed_path_ids = []
    for path_id in evopic.paths_order:
        if evopic.paths[path_id].type != "x":
            closed_path_ids.append(path_id)

    # Stop splits
    num_changes = num_mutations(mutation_rates["stop_split"], len(stop_locations))
    split_ids = []
    while num_changes > 0:
        num_changes -= 1
        path_id, pick_stop = choice(stop_locations)
        new_stop = copy(evopic.paths[path_id].stops[pick_stop])
        if new_stop["stop_id"] < 0 or new_stop["stop_id"] in split_ids:
            continue  # in the unlikely event that a new stop is selected for another split, try again.

        split_ids.append(new_stop["stop_id"])
        # Set stop ID to negative of its parent, then I can hook onto neg IDs when it's time to save the new evopic
        new_stop["stop_id"] *= -1
        stop_position = choice([pick_stop, pick_stop + 1])
        evopic.paths[path_id].stops.insert(stop_position, new_stop)

    stop_locations = evopic.stop_locations()

    # Stop deletions. Min # stops per path is 1.
    num_changes = num_mutations(mutation_rates["del_stop"], len(stop_locations) - len(closed_path_ids))
    while num_changes > 0:
        deletable_stops = []
        for path_id in evopic.paths_order:
            if len(evopic.paths[path_id].stops) > 1:
                for stop_index in range(len(evopic.paths[path_id].stops)):
                    deletable_stops.append((path_id, stop_index))

        deleted_stop = choice(deletable_stops)
        del evopic.paths[deleted_stop[0]].stops[deleted_stop[1]]
        num_changes -= 1

    stop_locations = evopic.stop_locations()

    # Len(path_ids) below is * 2 because they can be radial or linear
    num_changes = num_mutations(mutation_rates["gradient_param"], len(closed_path_ids) * 2)
    while num_changes > 0:
        path_id = choice(closed_path_ids)
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

    # Mutate the stop parameters
    num_changes = num_mutations(mutation_rates["stop_params"], len(stop_locations))
    while num_changes > 0:
        path_id, stop_pos = choice(stop_locations)
        path = evopic.paths[path_id]
        stop = path.stops[stop_pos]

        position = choice((0, 1, 2))
        if position == 0:
            stop["params"][0] = mutate_color(stop["params"][0])

        else:
            stop["params"][position] = move_in_range(stop["params"][position], [0., 1.], magnitudes["stop_params"])

        path.stops[stop_pos] = stop
        num_changes -= 1

    # Path splits. Cuts a path into two pieces, joining each exposed end to its partner if the path is closed,
    # or just slicing it otherwise.
    # Note that the larger of the two halves gets to keep the original path ID
    num_changes = num_mutations(mutation_rates["path_split"], len(evopic.paths_order))
    split_ids = []
    while num_changes > 0:
        num_changes -= 1  # decrement num_changes early to prevent infinite loops
        path_id, point_id1 = choice(evopic.point_locations())

        if path_id < 0 or (path_id in split_ids):  # In case a path has already been split, skip
            continue

        split_ids.append(path_id)
        path = evopic.paths[path_id]

        if path.id < 0:
            print(path, "\n")
            print(path_id, point_id1)
            sys.exit()

        if len(path.points) == 1:  # Can't split a path with only one point.
            continue

        new_path = copy(path)
        new_path.id *= -1

        new_path.points = {}
        point_index = path.points_order.index(point_id1)

        if path.type == "x":
            if point_index in [0, (len(path.points_order) - 1)]:
                new_path.points_order = [point_id1]
                new_path.points[point_id1] = path.points[point_id1]
                evopic.delete_point(path_id, point_id1)

            else:
                new_position = choice([point_index, point_index + 1])
                if len(path.points_order[new_position:]) < (len(path.points_order) / 2):
                    new_path.points_order = path.points_order[new_position:]

                else:
                    new_path.points_order = path.points_order[:new_position]

                for point_id in new_path.points_order:
                    new_path.points[point_id] = path.points[point_id]
                    evopic.delete_point(path_id, point_id)

        else:
            # This next bit is for closed paths, where a second point has to be chosen for the split to cut through
            while True:
                point_id2 = choice(path.points_order)
                if point_id1 == point_id2:
                    continue
                else:
                    break

            # Get the points in order from left to right
            point1_index, point2_index = [path.points_order.index(point_id1), path.points_order.index(point_id2)]
            point1_index, point2_index = [min(point1_index, point2_index), max(point1_index, point2_index)]
            point_id1, point_id2 = [path.points_order[point1_index], path.points_order[point2_index]]

            if len(path.points_order) > 3:
                outer_path = path.points_order[:point1_index] + path.points_order[point2_index + 1:]
                inner_path = path.points_order[point1_index:point2_index + 1]

            elif len(path.points_order) == 3:
                outer_path = [point_id1, point_id2]
                for point_id in path.points_order:
                    if point_id in outer_path:
                        continue
                    else:
                        inner_path = [point_id]

            elif len(path.points_order) == 2:
                outer_path = [point_id1]
                inner_path = [point_id2]

            else:
                sys.exit("There is an error in closed path splitting")

            if len(outer_path) >= len(inner_path):
                new_path.points_order = inner_path

            else:
                new_path.points_order = path.points_order[:point1_index + 1] + path.points_order[point2_index:]

            for point_id in new_path.points_order:
                new_path.points[point_id] = path.points[point_id]
                evopic.delete_point(path_id, point_id)

        order_index = evopic.paths_order.index(path_id)

        new_position = choice([order_index, order_index + 1])
        evopic.paths[new_path.id] = new_path
        evopic.paths_order.insert(new_position, new_path.id)

    evopic.find_extremes()
    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/sue.evp", "r") as infile:
        bob = Evopic(infile.read())