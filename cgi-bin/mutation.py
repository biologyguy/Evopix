#!/usr/bin/python3
from Evopic import Evopic


def number_of_mutations(sample_size, probability):  # This is going to return a value from a poisson distribution
    return "Some number"


def mutate(evopic):
    for path_id in evopic.paths_z_pos:
        print(path_id)
    return evopic

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        bob = mutate(bob)
        print(bob.svg_out())

    with open("../genomes/test.svg", "w") as ofile:
        ofile.write(bob.svg_out())