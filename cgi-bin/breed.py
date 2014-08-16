#! /usr/bin/python
__author__ = 'bondsr'
from Evopic import Evopic
import math


def breed(evp1, evp2):
    """Notes:-The original evp file (i.e., not zeroed) needs to be used for breeding. Store the zeroed evp for printing.
             -When calculating thr min radius of radial stops, do not go below 0.002 (it breaks the fill)
             -Not sure if best to pass in evp files or evopic objects. Probably objects...
    """
    return


def zero_evp(evp):
    """New Evopix are able to wander around Cartesian space, which means they would start to wander off the canvas
    pretty quickly if we print the SVG true to their actual genome coords. Instead, create a separate evp file that
    finds the bounding box of the image and positions it close to 0,0. It's important to still breed from the original
    non-zeroed evp though, because a mutation on the extreme left of top of the image will result in new values for all
    coords, making it look like much more divergence between parent and offspring than there really is."""
    evopic = Evopic(evp)
    min_x, min_y, min_x_seq, min_y_seg = [9999999999.9, 9999999999.9, [], []]  # arbitrarily set large min values

    # convert the 'control-point-control' points format of the paths into 'point-control-control-point' line segments for bezier calc
    points = evopic.loop_paths("points")
    path_ids = evopic.loop_paths("path_id")

    count = 0
    for point in points:
        line_segments = []
        if not path_ids[count][-1] == "x":  # Do this if the path is closed
            for i in range(len(point)):
                if i + 1 == len(point):
                    line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[0]['coords'][0], point[0]['coords'][1]])
                else:
                    line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[i + 1]['coords'][0], point[i + 1]['coords'][1]])
        else:  # Do this for open paths
            for i in range(len(point)):
                if i + 1 == len(point):
                    continue
                else:
                    line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[i + 1]['coords'][0], point[i + 1]['coords'][1]])

        for seg in line_segments:

            bezier_bounds = (get_curve_bounds(seg[0][0], seg[0][1], seg[1][0], seg[1][1], seg[2][0], seg[2][1], seg[3][0], seg[3][1]))

            min_x = bezier_bounds['left'] if bezier_bounds['left'] < min_x else min_x
            min_y = bezier_bounds['top'] if bezier_bounds['top'] < min_y else min_y

        count += 1

    #adujust min x,y so they are not perfectly 0. Giving a little bit of margin looks nicer.
    min_x, min_y = [min_x - 3, min_y - 3]
    path_count = 0
    for path in evopic.paths:
        point_count = 0
        for point in path['points']:
            coords_count = 0
            for coords in point['coords']:
                coords[0] = coords[0] - min_x
                coords[1] = coords[1] - min_y

                evopic.paths[path_count]['points'][point_count]['coords'][coords_count] = [round(coords[0], 4),
                                                                                           round(coords[1], 4)]
                coords_count += 1
            point_count += 1
        path_count += 1

    evopic.reconstruct_evp()
    return evopic.evp


def get_curve_bounds(x0, y0, x1, y1, x2, y2, x3, y3):
    """Calculates the extreme points of a cubic Bezier curve
    Source: http://blog.hackers-cafe.net/2009/06/how-to-calculate-bezier-curves-bounding.html
    Original version: NISHIO Hirokazu
    Modifications: Timo
    Convert to Python: Steve Bond"""

    tvalues = []
    bounds = {"X": [], "Y": []}

    for i in range(2):
        if i == 0:
            b = 6. * x0 - 12. * x1 + 6. * x2
            a = -3. * x0 + 9. * x1 - 9. * x2 + 3. * x3
            c = 3. * x1 - 3. * x0

        else:
            b = 6. * y0 - 12. * y1 + 6. * y2
            a = -3. * y0 + 9. * y1 - 9. * y2 + 3. * y3
            c = 3. * y1 - 3. * y0

        if abs(a) < 0.0000000000001:  # Numerical robustness
            if abs(b) < 0.0000000000001:  # Numerical robustness
                continue

            t = -c / b

            if 0 < t < 1:
                tvalues.append(t)

            continue

        b2ac = b * b - 4. * c * a
        sqrtb2ac = math.sqrt(b2ac)
        if b2ac < 0:
            continue

        t1 = (-b + sqrtb2ac) / (2. * a)
        if 0 < t1 < 1:
            tvalues.append(t1)

        t2 = (-b - sqrtb2ac) / (2. * a)
        if 0 < t2 < 1:
            tvalues.append(t2)

    j = len(tvalues)

    while j > 0:
        j -= 1
        t = tvalues[j]
        mt = 1. - t
        x = (mt * mt * mt * x0) + (3. * mt * mt * t * x1) + (3. * mt * t * t * x2) + (t * t * t * x3)
        bounds["X"].append(x)

        y = (mt * mt * mt * y0) + (3. * mt * mt * t * y1) + (3. * mt * t * t * y2) + (t * t * t * y3)
        bounds["Y"].append(y)

    bounds["X"].append(x0)
    bounds["Y"].append(y0)
    bounds["X"].append(x3)
    bounds["Y"].append(y3)
    return {"left": round(min(bounds["X"]), 4), "top": round(min(bounds["Y"]), 4), "right": round(max(bounds["X"]), 4),
            "bottom": round(max(bounds["Y"]), 4)}


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    #bounds = get_curve_bounds(532, 333, 117, 305, 28, 93, 265, 42)
    #Prints: {"left":135.77684,"top":42,"right":532,"bottom":333,"points":[{"X":135.77684049079755,"Y":144.86387466397255},{"X":532,"Y":333},{"X":265,"Y":42}],"tvalues":[0.6365030674846626,0,1]}

    #bounds = get_curve_bounds(88.9514, 320.4029, 31.6589, 281.0587, 0.7516, 223.7982, 12.5989, 163.8201)
    #print(bounds)
    blahh = {'right': 88.9514, 'top': 163.8201, 'left': 10.091368, 'bottom': 320.4029}

    with open("../genomes/bob.evp", "r") as infile:
        #print(zero_evp(infile.read()))
        bob = Evopic(zero_evp(infile.read()))
        print(bob.svg_out())
