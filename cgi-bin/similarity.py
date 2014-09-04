#!/usr/bin/python3
from Evopic import Evopic

def similarity_score(evo1, evo2):
    sim_score = 0.

    #Match path IDs
    evo1_path_ids = []
    for path in evo1.paths:
        evo1_path_ids.append(int(path["path_id"][:-1]))

    evo2_path_ids = []
    for path in evo2.paths:
        evo2_path_ids.append(int(path["path_id"][:-1]))

    for id in evo1_path_ids:
        if id in evo2_path_ids:
            print evo2_path_ids.index(id)

    return sim_score


#------------- Sandbox ----------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())

    with open("../genomes/bubba.evp", "r") as infile:
        sue = Evopic(infile.read())

    print(similarity_score(bob, sue))