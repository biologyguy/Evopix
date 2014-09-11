#! /usr/bin/python
from argparse import (ArgumentParser, FileType)
from Evopic import Evopic
import random

def parse_args():

    parser = ArgumentParser(description='Create paths for a new offspring from mum and dad')

    parser.add_argument('--mother', type=str, required=False, help='Mother evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/sue.evp')
    parser.add_argument('--father', type=str, required=False, help='Father evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/bob.evp')

    return parser.parse_args()

def main():

    args = parse_args()

    with open(args.father, 'r') as infile:
        boy = Evopic(infile.read())
    with open(args.mother, 'r') as infile:
        girl = Evopic(infile.read())

    random.seed(10)
    prop = random.randrange(0, 100, 1)
    prop = prop / 100
    print(prop)

    for path_id in boy.paths:
        if path_id in girl.paths:
            for coordinate_set in boy.paths[path_id]['points']:
                print(coordinate_set['coords'])
                coord_no = 0
                for coord in coordinate_set['coords']:
                    #this line doesn't allow me to get to the correct coord for the girl evopic... I'm getting lost
                    #in my parsing!
                    new_coord = (coord[0] * prop + girl.paths[path_id]['points'][coordinate_set.index()]['coords'][0] * prop)
                    print(new_coord) 
                
if __name__ == '__main__':
    main()

