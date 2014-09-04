#!/usr/bin/python3
from Evopic import Evopic


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

    return sim_score


#------------- Sandbox ----------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())

    with open("../genomes/bubba.evp", "r") as infile:
        sue = Evopic(infile.read())

    print("%s\n" % similarity_score(bob, sue))

    for i in bob.paths[1]:
        print("%s: %s" % (i, bob.paths[1][i]))