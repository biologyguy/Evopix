#! /usr/bin/python
from argparse import (ArgumentParser, FileType)
from Evopic import Evopic
import random
import sys

def parse_args():

    parser = ArgumentParser(description='Create paths for a new offspring from mum and dad')

    parser.add_argument('--mother', type=str, required=False, help='Mother evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/bubba.evp')
    parser.add_argument('--father', type=str, required=False, help='Father evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/bob.evp')

    #parser.add_argument('--mother', type=str, required=False, help='Mother evopic to breed with', default='/var/www/Evopix/genomes/sue.evp')
    #parser.add_argument('--father', type=str, required=False, help='Father evopic to breed with', default='/var/www/Evopix/genomes/bob.evp')

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

    #--------Try looping something like this--------#
    mismatch_paths = {'girl': [], 'boy': []}
    included_paths = {'girl': [], 'boy': []}

    for path_id in girl.paths_order:
        if path_id not in boy.paths_order:
            mismatch_paths['girl'].append(path_id)
    for path_id in boy.paths_order:
        if path_id not in girl.paths_order:
            mismatch_paths['boy'].append(path_id)
            continue
        
        boy_path = boy.paths[path_id]
        girl_path = girl.paths[path_id]
        print("Boy path ID:%s\nPoint IDs\tCoords" % path_id)
        for point_id in boy_path.points_order:
            coords = boy_path.points[point_id]
            print("\t%s\t\t%s" % (point_id, coords))
        flip = random.randint(0, 1)
        if flip == 1:
            included_paths['boy'].append(path_id)
        else:
            included_paths['girl'].append(path_id)

    for path in mismatch_paths['girl']:
        flip = random.randint(0, 1)
        if flip == 1:
            included_paths['girl'].append(path)
    for path in mismatch_paths['boy']:
        flip = random.randint(0, 1)
        if flip == 1:
            included_paths['boy'].append(path)
    print(included_paths)

    new_path_set = []
    new_path_order = []

    for path in included_paths['boy']:
        new_path_set.append(boy.paths[path])
        new_path_order.append(path)
    for path in included_paths['girl']:
        new_path_set.append(girl.paths[path])
        new_path_order.append(path)
    print(new_path_set)
    print(new_path_order)

    baby = ''
    print(new_path_set[2])
    for path_id in new_path_order:
        print(path_id)
        path = new_path_set[path_id]
        baby += "p%s%s:" % (path.id, path.type)
        for point_id in path.points_order:
            coords = path.points[point_id]
            baby += "t%s~%s,%s;%s,%s;%s,%s;" % (point_id, coords[0][0], coords[0][1], coords[1][0],
                                                   coords[1][1], coords[2][0], coords[2][1])

        if path.type in ["r", "l"]:  # skip if the path is not closed
            baby += ":r,%s,%s,%s,%s,%s" % tuple(path.radial)
            baby += ":l,%s,%s,%s,%s:" % tuple(path.linear)

            for stop in path.stops:
                params = stop["params"]
                baby += "o%s~%s,%s,%s;" % (stop["stop_id"], params[0], params[1], params[2])

        baby += ":s%s,%s,%s\n" % tuple(path.stroke)
    baby_evo = Evopic(baby)
    print(baby_evo)



    sys.exit("Exit at line 49")
    #------------------------------------------------#

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
                
if __name__ == '__main__':
    main()


