#!/usr/bin/python3
from Evopic import Evopic


def similarity_score(evo_1, evo_2):
    """
    Weightings: - Path presence/absence (weighted by size)
                - Path similarity between shared paths

    """
    sim_score = 1.

    #Match path IDs, and subtract the size of non-shared paths
    evo_1_path_ids = []
    evo_1_path_sizes = []
    for path in evo_1.paths:
        evo_1_path_ids.append(int(path["path_id"][:-1]))
        evo_1_path_sizes.append(len(path["points"]))

    evo_2_path_ids = []
    evo_2_path_sizes = []
    for path in evo_2.paths:
        evo_2_path_ids.append(int(path["path_id"][:-1]))
        evo_2_path_sizes.append(len(path["points"]))

    matched_paths = []
    for path_id in list(evo_1_path_ids):
        if path_id in evo_2_path_ids:
            matched_paths.append(path_id)
            del evo_1_path_ids[evo_1_path_ids.index(path_id)]
            del evo_2_path_ids[evo_2_path_ids.index(path_id)]

    print(evo_1_path_sizes)
    print(evo_2_path_sizes)
    print(matched_paths)

    return sim_score


#------------- Sandbox ----------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())

    with open("../genomes/bubba.evp", "r") as infile:
        sue = Evopic(infile.read())

    print(similarity_score(bob, sue))

    for i in bob.paths[0]:
        print("%s: %s" % (i, bob.paths[0][i]))