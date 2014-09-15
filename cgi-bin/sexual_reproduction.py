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

    #print(boy.paths[1].points)

    for path in boy.paths:
        boy_points = boy.paths[path].points
        girl_points = girl.paths[path].points
        baby_points = []
        for coord_set in range(0, len(boy_points)):
            coord_list = boy_points[coord_set]['coords']
            point_id = boy_points[coord_set]['point_id']
            if point_id == girl_points[coord_set]['point_id']:
                new_coords = []
                coord_index = 0
                for coord in coord_list:
                    new_point = [round((coord[0] * prop), 4) + round((girl_points[coord_set]['coords'][coord_index][0] * prop), 4), 
                                round((coord[1] * prop),4) + round((girl_points[coord_set]['coords'][coord_index][1]), 4)]
                    coord_index += 1
                    new_coords.append(new_point)
                new_coord_set = {}
                new_coord_set['coords'] = new_coords
                new_coord_set['point_id'] = point_id
            baby_points.append(new_coord_set)
        print(new_coord_set)
    print(baby_points)


            #print('this is the boys')
            #print(coord_list)
            #print('this is the corresponding girls')
            #print(girl_points[coord_set]['coords'])



    '''for path_id in boy.paths:
        if path_id in girl.paths:
            for coordinate_set in boy.paths[path_id]['points']:
                print(coordinate_set['coords'])
                coord_no = 0
                for coord in coordinate_set['coords']:
                    #this line doesn't allow me to get to the correct coord for the girl evopic... I'm getting lost
                    #in my parsing!
                    new_coord = (coord[0] * prop + girl.paths[path_id]['points'][coordinate_set.index()]['coords'][0] * prop)'''
                    #print(new_coord) 
                
if __name__ == '__main__':
    main()

