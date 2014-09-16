#! /usr/bin/python
from argparse import (ArgumentParser, FileType)
from Evopic import Evopic
from Evopic import Path
import random
import sys

def parse_args():

    parser = ArgumentParser(description='Create paths for a new offspring from mum and dad')

    parser.add_argument('--mother', type=str, required=False, help='Mother evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/bubba.evp')
    parser.add_argument('--father', type=str, required=False, help='Father evopic to breed with', default='/Users/jane/Documents/scripts_local/Evopix/genomes/bob.evp')
    parser.add_argument('--out', type=str, required=False, help='new evopic svg', default='/Users/jane/Documents/scripts_local/Evopix/genomes/baby')

    #parser.add_argument('--mother', type=str, required=False, help='Mother evopic to breed with', default='/var/www/Evopix/genomes/sue.evp')
    #parser.add_argument('--father', type=str, required=False, help='Father evopic to breed with', default='/var/www/Evopix/genomes/bob.evp')

    return parser.parse_args()

def weighting(boy_coords, girl_coords, weight):

    x_boy = boy_coords[0]
    y_boy = boy_coords[1]
    z_boy = boy_coords[2]
    x_girl = girl_coords[0]
    y_girl = girl_coords[1]
    z_girl = girl_coords[2]

    new_x = [round(x_boy[0] * weight, 4) + round(x_girl[0] * weight, 4), round(x_boy[1] * weight, 4) + round(x_girl[1] * weight, 4)]
    new_y = [round(y_boy[0] * weight, 4) + round(y_girl[0] * weight, 4), round(y_boy[1] * weight, 4) + round(y_girl[1] * weight, 4)]
    new_z = [round(z_boy[0] * weight, 4) + round(z_girl[0] * weight, 4), round(z_boy[1] * weight, 4) + round(z_girl[1] * weight, 4)] 

    new_coord_set = [new_x, new_y, new_z]
    return new_coord_set

def main():

    args = parse_args()

    with open(args.father, 'r') as infile:
        boy = Evopic(infile.read())
    with open(args.mother, 'r') as infile:
        girl = Evopic(infile.read())

    #random.seed(10)
    prop = random.randrange(0, 100, 1)
    prop = prop / 100
    print(prop)

    #print(boy.paths[1].points)

    #--------Try looping something like this--------#
    mismatch_paths = {'girl': [], 'boy': []}
    included_paths = {'girl': [], 'boy': []}
    new_path_set = []
    new_path_order = []

    for path_id in girl.paths_order:
        if path_id not in boy.paths_order:
            mismatch_paths['girl'].append(path_id)
    for path_id in boy.paths_order:

        if path_id not in girl.paths_order:
            mismatch_paths['boy'].append(path_id)
            continue
        
        boy_path = boy.paths[path_id]
        girl_path = girl.paths[path_id]

        new_path = Path()
        new_path_id = path_id
        new_path.id = new_path_id
        new_path.type = boy_path.type
        points_dict = {}
        points_order = []
        print(boy_path.type)
        print("Boy path ID:%s\nPoint IDs\tCoords" % path_id)
        for point_id in boy_path.points_order:
            coords = boy_path.points[point_id]
            if point_id in girl_path.points:
                new_coords = weighting(coords, girl_path.points[point_id], prop)
                points_dict[point_id] = new_coords
                points_order.append(point_id)
                print("\t%s\t\t%s" % (point_id, new_coords))

        # add converted points to new path for baby
        new_path.points = points_dict
        new_path.points_order = points_order

        # get radial points if required
        new_radial = []
        if len(boy_path.radial) != 0:
            for point in range(0, len(boy_path.radial)):
                new_point = round(boy_path.radial[point] * prop, 1) + round(girl_path.radial[point] * prop, 1)
                new_radial.append(new_point)
            # add converted radial points to new path for baby
            new_path.radial = new_radial
        print('babys new radial')
        print(new_radial)
        
        # get linear points if required
        new_linear = []
        if len(boy_path.linear) != 0:
            for point in range(0, len(boy_path.linear)):
                new_point = round(boy_path.linear[point] * prop, 1) + round(girl_path.radial[point] * prop, 1)
                new_linear.append(new_point)
            # add converted linear points to new path for baby
            new_path.linear = new_linear
        print('babys new linear')
        print(new_linear)

        # get stroke if required
        new_stroke = []
        if len(boy_path.stroke) != 0:
            flip = random.randint(0, 1)
            if flip == 1:
                new_stroke = boy_path.stroke
            else:
                new_stroke = girl_path.stroke
            # add selected stroke to path for baby
            new_path.stroke = new_stroke
        print('babys new stroke')
        print(new_stroke)

        # get stops if required
        new_stops = []
        if len(boy_path.stops) != 0:
            flip = random.randint(0, 1)
            if flip == 1:
                new_stops = boy_path.stops
            else:
                new_stops = girl_path.stops
            # add selected stops to path for baby
            new_path.stops = new_stops
        print('babys new stops')
        print(new_stops)

        new_path_set.append(new_path)

    for path in mismatch_paths['girl']:
        flip = random.randint(0, 1)
        if flip == 1:
            #included_paths['girl'].append(path)
            new_path_set.append(girl.paths[path])
            new_path_order.append(path)
    for path in mismatch_paths['boy']:
        flip = random.randint(0, 1)
        if flip == 1:
            included_paths['boy'].append(path)
            new_path_set.append(boy.paths[path])
            new_path_order.append(path)
    #print(included_paths)

    print(new_path_set)
    print(new_path_order)

    baby = ''
    #print(new_path_set[2])
    for path in new_path_set:
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
    with open(args.out + '.evp', 'w') as f:
        f.write(baby)

    out_svg = baby_evo.svg_out()

    with open(args.out + '.svg', 'w') as f:
        f.write(out_svg)

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


