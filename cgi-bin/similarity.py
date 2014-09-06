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
    del path["points"][0]
    for i in path["points"]:
        length += line_length([ox, oy], i["coords"][1])
        ox, oy = i["coords"][1]
    return length

def line_length(point_a, point_b):  # implement Pythagorean theorem
    length = (abs(point_a[0] - point_b[0])**2 + abs(point_a[1] - point_b[1])**2)**0.5
    return length


def match_path_points(path_1, path_2):
    """
    Returns the abs differences between control-point-control points for all matched points in the paths, and counts
    the number of unmatched points
    :rtype : {"matched": [], "unmatched": int}
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
    Weightings: - Path presence/absence (weighted by size)
                - Path similarity between shared paths
    """
    sim_score = 1.

    #Match path IDs, and account for non-shared paths
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

    sim_score *= float(matched_points)/float(total_points)

    #Run through each matched path, and get the weighted average (based on number of points) sim score.
    total_point_count = 0
    path_sim_info = {"ids": [], "num_points": [], "sim_scores": []}
    for path_id in matched_paths:
        path_1, path_2 = [evo_1.paths[path_id], evo_2.paths[path_id]]
        # For closed paths, the size of the path is based on area
        if evo_1.paths[path_id]["type"] in ["r", "l"]:
            ave_path_area = (find_path_area(path_1) + find_path_area(path_2))/2.
            path_size = ave_path_area ** 0.5  # Used to assess the magnitude of differences between points

            num_points_in_paths = len(path_1["points"]) + len(path_2["points"])
            total_point_count += num_points_in_paths

            path_sim_info["ids"].append(path_id)
            path_sim_info["num_points"].append(num_points_in_paths)

            point_matches = match_path_points(path_1, path_2)

            matches_sim_score = sum(point_matches["matches"])/len(point_matches["matches"])
            matches_sim_score = 1. - (matches_sim_score/(matches_sim_score + path_size))

            final_points_sim_score = matches_sim_score * (1. - (point_matches["unmatched"] / num_points_in_paths))
            print(final_points_sim_score)

        # For open paths, the size is based on total path length
        else:
            print(find_path_length(path_1))
            #ave_path_length = (find_path_length(path_1) + find_path_length(path_2))/2.


        #break
    return sim_score


#------------- Sandbox ----------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())

    with open("../genomes/bubba.evp", "r") as infile:
        sue = Evopic(infile.read())

    print("\n%s\n" % similarity_score(bob, sue))

    print(bob.paths[1]["points"])

