#!/usr/bin/python3
from Evopic import Evopic
import sys


def find_path_area(path):  # Input is an individual path from Evopic.paths
    """
    Modified from http://www.arachnoid.com/area_irregular_polygon/index.html
    Calculates the area of an irregular polygon using the sum of the cross products of each neighboring pair of coords.
    It's super nice, because it scales at N.
    """
    array = []
    for i in path["points"]:
        array.append(i["coords"][1])

    area = 0
    ox, oy = array[-1]  # set the 'first' point as the same as the last point, to close the path
    for x, y in array:
        area += (x * oy - y * ox)
        ox, oy = x, y
    return abs(area/2)


def find_path_length(path):  # Input is an individual path from Evopic.paths
    length = 0.
    ox, oy = path["points"][0]["coords"][1]
    for i in path["points"][1:]:
        length += line_length([ox, oy], i["coords"][1])
        ox, oy = i["coords"][1]
    return length


def line_length(point_a, point_b):  # implement Pythagorean theorem
    length = (abs(point_a[0] - point_b[0])**2 + abs(point_a[1] - point_b[1])**2)**0.5
    return length


def colour_diff(stroke_1, stroke_2):
    r1 = int(stroke_1[:2], 16)
    r2 = int(stroke_2[:2], 16)
    g1 = int(stroke_1[2:4], 16)
    g2 = int(stroke_2[2:4], 16)
    b1 = int(stroke_1[4:], 16)
    b2 = int(stroke_2[4:], 16)
    output = 1.
    output -= abs(r1 - r2)/255 * (1./3.)
    output -= abs(g1 - g2)/255 * (1./3.)
    output -= abs(b1 - b2)/255 * (1./3.)

    return output


def match_path_points(path_1, path_2):
    """
    Returns the abs differences between control-point-control points for all matched points in the paths, and counts
    the number of unmatched points
    :rtype : {"matched": [floats], "unmatched": int}
    :param path_1: Evopic.paths[<path_id>] 
    :param path_2: Evopic.paths[<path_id>] matched to path_1
    """
    path_1_dict, path_2_dict, path_2_ids = {}, {}, []
    for point in path_1["points"]:
        path_1_dict[point["point_id"]] = point["coords"]

    for point in path_2["points"]:
        path_2_dict[point["point_id"]] = point["coords"]
        path_2_ids.append(point["point_id"])

    output = {"matches": [], "unmatched": 0}

    for point_id in path_1_dict:
        if point_id in path_2_ids:
            pt_1 = path_1_dict[point_id]
            pt_2 = path_2_dict[point_id]

            output["matches"].append(line_length(pt_1[0], pt_2[0]))
            output["matches"].append(line_length(pt_1[1], pt_2[1]))
            output["matches"].append(line_length(pt_1[2], pt_2[2]))

            del path_2_ids[path_2_ids.index(point_id)]

        else:
            output["unmatched"] += 1

    output["unmatched"] += len(path_2_ids)
    return output


def similarity_score(evo_1, evo_2):
    """
    Weightings: -   Path points, 60% total weighting for closed paths, and 80% for lines. Each path is weighted
                    according to size. Where a path is present in one and not the other, a value of 0% equivalent is
                    applied
                -   Stroke size contributes 10% to closed paths, and 20% to lines
                -   Gradients each contribute 5%
                -   Stops contribute 20%
    """
    #Match path IDs, and count # points so similarity can be weighted to path sizes
    total_points = 0
    matched_points = 0
    matched_paths = []
    for path_id in evo_1.paths_z_pos:
        total_points += len(evo_1.paths[path_id]["points"])

        if path_id in evo_2.paths_z_pos:
            matched_points += len(evo_1.paths[path_id]["points"]) + len(evo_2.paths[path_id]["points"])
            matched_paths.append(path_id)

    for path_id in evo_2.paths_z_pos:
        total_points += len(evo_2.paths[path_id]["points"])

    #Run through each matched path, and get the weighted average (based on number of points) sim score.
    path_sim_info = {"ids": [], "num_points": [], "point_sim_scores": [], "stroke_sim_scores": [],
                     "gradient_sim_scores": [], "stop_sim_scores": []}

    for path_id in matched_paths:
        path_sim_info["ids"].append(path_id)

        path_1, path_2 = [evo_1.paths[path_id], evo_2.paths[path_id]]

        # For closed paths, the size of the path is based on area
        if path_1["type"] in ["r", "l"]:
            ave_path_area = (find_path_area(path_1) + find_path_area(path_2))/2.
            path_size = ave_path_area ** 0.5  # Used to assess the magnitude of differences between points

        # For open paths, the size is based on total path length
        else:
            path_size = (find_path_length(path_1) + find_path_length(path_2))/2.

        num_points_in_paths = len(path_1["points"]) + len(path_2["points"])
        path_sim_info["num_points"].append(num_points_in_paths)

        point_matches = match_path_points(path_1, path_2)

        matches_sim_score = sum(point_matches["matches"])/len(point_matches["matches"])
        matches_sim_score = 1. - (matches_sim_score/(matches_sim_score + path_size))
        final_points_sim_score = matches_sim_score * (1. - (point_matches["unmatched"] / num_points_in_paths))
        path_sim_info["point_sim_scores"].append(final_points_sim_score)

        # Stroke similarity (colour = 47.5%, opacity = 17.5%, width = 35%)
        colour = colour_diff(path_1["stroke"][0], path_2["stroke"][0])
        opacity = 1. - abs(path_1["stroke"][2] - path_2["stroke"][2])
        width = 1. - abs(path_1["stroke"][1] - path_2["stroke"][1])/(path_1["stroke"][1] + path_2["stroke"][1])

        path_sim_info["stroke_sim_scores"].append((0.475 * colour) + (0.175 * opacity) + (0.35 * width))

        # Gradients and stops are only in closed paths
        if path_1["type"] in ["r", "l"]:
            p1_grad_attribs = path_1["radial"] + path_1["linear"]
            p2_grad_attribs = path_2["radial"] + path_2["linear"]
            grad_sim = 1.
            for i in range(len(p1_grad_attribs)):
                grad_sim -= abs(p1_grad_attribs[i] - p2_grad_attribs[i])/len(p1_grad_attribs)

            path_sim_info["gradient_sim_scores"].append(grad_sim)

            # getting stop info is going to be similar to getting num paths or points
            stops_1_dict, stops_2_dict, stops_2_ids = {}, {}, []

            for stop in path_1["stops"]:
                stops_1_dict[stop["stop_id"]] = stop["params"]

            for stop in path_2["stops"]:
                stops_2_dict[stop["stop_id"]] = stop["params"]
                stops_2_ids.append(stop["stop_id"])

            output = {"matches": [], "unmatched": 0}

            for stop_id in stops_1_dict:
                if stop_id in stops_2_ids:
                    output["matches"].append(stops_1_dict[stop_id][0])
                    output["matches"].append(stops_1_dict[stop_id][1])
                    output["matches"].append(stops_1_dict[stop_id][2])

                    del stops_2_ids[stops_2_ids.index(stop_id)]

                else:
                    output["unmatched"] += 1

            output["unmatched"] += len(stops_2_ids)
            print(output)
            sys.exit()
            path_sim_info["stop_sim_scores"].append(True)

        else:
            path_sim_info["gradient_sim_scores"].append(False)
            path_sim_info["stop_sim_scores"].append(False)

    # Add it all together
    sim_score = 0.
    for i in range(len(path_sim_info["ids"])):
        weight = path_sim_info["num_points"][i] / total_points

        if evo_1.paths[path_sim_info["ids"][i]]["type"] in ["r", "l"]:
            # points
            sim_score += weight * path_sim_info["point_sim_scores"][i] * 0.6

            # strokes
            sim_score += weight * path_sim_info["stroke_sim_scores"][i] * 0.1

            # gradients
            sim_score += weight * path_sim_info["gradient_sim_scores"][i] * 0.1

            #stops
            sim_score += weight * 0.0 * 0.2

        else:
            # points
            sim_score += weight * path_sim_info["point_sim_scores"][i] * 0.8

            # strokes
            sim_score += weight * path_sim_info["stroke_sim_scores"][i] * 0.2

    return sim_score


#------------- Sandbox ----------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())

    with open("../genomes/sue.evp", "r") as infile:
        sue = Evopic(infile.read())

    print("Similarity score\n%s\n" % similarity_score(bob, sue))

    print(bob.paths[1]["stops"])
