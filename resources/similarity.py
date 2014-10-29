#!/usr/bin/python3
try:
    from Evo import *

except ImportError:
    from resources.Evo import *
    from evp.models import *


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
    output = {"matches": [], "unmatched": 0}

    for point_id in path_1.points_order:
        if point_id in path_2.points_order:
            pt_1 = path_1.points[point_id]
            pt_2 = path_2.points[point_id]

            output["matches"].append(LineSeg(pt_1[0], pt_2[0]).length())
            output["matches"].append(LineSeg(pt_1[1], pt_2[1]).length())
            output["matches"].append(LineSeg(pt_1[2], pt_2[2]).length())

        else:
            output["unmatched"] += 1

    output["unmatched"] += len(path_2.points_order) - (len(output["matches"]) / 3.)
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
    for path_id in evo_1.paths_order:
        path_1, path_2 = [evo_1.paths[path_id], evo_2.paths[path_id]]
        total_points += len(path_1.points)

        if path_id in evo_2.paths_order:
            matched_points += len(path_1.points) + len(path_2.points)
            matched_paths.append(path_id)

    for path_id in evo_2.paths_order:
        total_points += len(evo_2.paths[path_id].points)

    #Run through each matched path, and get the weighted average (based on number of points) sim score.
    path_sim_info = {"ids": [], "num_points": [], "point_sim_scores": [], "stroke_sim_scores": [],
                     "gradient_sim_scores": [], "stop_sim_scores": []}

    for path_id in matched_paths:
        path_sim_info["ids"].append(path_id)

        path_1, path_2 = [evo_1.paths[path_id], evo_2.paths[path_id]]

        num_points_in_paths = len(path_1.points) + len(path_2.points)
        path_sim_info["num_points"].append(num_points_in_paths)

        point_matches = match_path_points(path_1, path_2)

        matches_sim_score = sum(point_matches["matches"])/len(point_matches["matches"])
        matches_sim_score = 1. - (matches_sim_score/(matches_sim_score + (path_1.path_size() + path_2.path_size())/2))
        final_points_sim_score = matches_sim_score * (1. - (point_matches["unmatched"] / num_points_in_paths))
        path_sim_info["point_sim_scores"].append(final_points_sim_score)

        # Stroke similarity (colour = 47.5%, opacity = 17.5%, width = 35%)
        colour = colour_diff(path_1.stroke[0], path_2.stroke[0])
        opacity = 1. - abs(path_1.stroke[2] - path_2.stroke[2])
        width = 1. - abs(path_1.stroke[1] - path_2.stroke[1])/(path_1.stroke[1] + path_2.stroke[1])

        path_sim_info["stroke_sim_scores"].append((0.475 * colour) + (0.175 * opacity) + (0.35 * width))

        # Gradients and stops are only in closed paths
        if path_1.type in ["r", "l"]:
            p1_grad_attribs = path_1.radial + path_1.linear
            p2_grad_attribs = path_2.radial + path_2.linear
            grad_sim = 1.
            for i in range(len(p1_grad_attribs)):
                grad_sim -= abs(p1_grad_attribs[i] - p2_grad_attribs[i])/len(p1_grad_attribs)

            path_sim_info["gradient_sim_scores"].append(grad_sim)

            # Stops similarity is divided between colour and position, 50% to each.
            stops_1_dict, stops_2_dict, stops_2_ids = {}, {}, []

            for stop in path_1.stops:
                stops_1_dict[stop["stop_id"]] = stop["params"]

            for stop in path_2.stops:
                stops_2_dict[stop["stop_id"]] = stop["params"]
                stops_2_ids.append(stop["stop_id"])

            stop_matches = {"matches": [], "unmatched": 0}

            for stop_id in stops_1_dict:
                if stop_id in stops_2_ids:
                    sim = 0.
                    sim += 0.5 * colour_diff(stops_1_dict[stop_id][0], stops_2_dict[stop_id][0])
                    sim += 0.25 * (1. - abs(stops_1_dict[stop_id][1] - stops_2_dict[stop_id][1]))
                    sim += 0.25 * (1. - abs(stops_1_dict[stop_id][2] - stops_2_dict[stop_id][2]))

                    stop_matches["matches"].append(sim)
                    del stops_2_ids[stops_2_ids.index(stop_id)]

                else:
                    stop_matches["unmatched"] += 1

            stop_matches["unmatched"] += len(stops_2_ids)
            path_sim_info["stop_sim_scores"].append(sum(stop_matches["matches"]) / (stop_matches["unmatched"]
                                                                                    + len(stop_matches["matches"])))

        else:
            path_sim_info["gradient_sim_scores"].append(False)
            path_sim_info["stop_sim_scores"].append(False)

    # Add it all together
    sim_score = 0.
    for i in range(len(path_sim_info["ids"])):
        weight = path_sim_info["num_points"][i] / total_points

        if evo_1.paths[path_sim_info["ids"][i]].type in ["r", "l"]:
            # points
            sim_score += weight * path_sim_info["point_sim_scores"][i] * 0.6

            # strokes
            sim_score += weight * path_sim_info["stroke_sim_scores"][i] * 0.1

            # gradients
            sim_score += weight * path_sim_info["gradient_sim_scores"][i] * 0.1

            # stops
            sim_score += weight * path_sim_info["stop_sim_scores"][i] * 0.2

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

    with open("../genomes/bubba.evp", "r") as infile:
        sue = Evopic(infile.read())

    print("Similarity score\n%s\n" % similarity_score(bob, sue))
