#! /usr/bin/python3
import sys
from evp.models import *
from world.models import *
from resources import mutation
from resources.LineSeg import *


class Evopic():
    def __init__(self, evp="", evo_id=0):
        self.evp = evp
        self.id = evo_id
        self.paths = {}
        self.paths_order = []
        self._num_points = 0
        self._point_locations = []
        self.min_max_points = {"min_x": 0., "min_y": 0., "max_x": 0., "max_y": 0.}
        self.health = None
        self.world_dimensions = None
        if evp != "":
            self._parse_evp()
        elif evo_id > 0:
            self._database()

    @staticmethod
    def world_xy(evo_id):
        land_units = LandUnit.objects.filter(evopic_id=evo_id)
        if len(land_units) == 0:
            return None

        min_x, min_y, max_x, max_y = 9999999999, 9999999999, 0, 0
        for land_unit in land_units:
            min_x = land_unit.x if land_unit.x < min_x else min_x
            min_y = land_unit.y if land_unit.y < min_y else min_y
            max_x = land_unit.x if land_unit.x > max_x else max_x
            max_y = land_unit.y if land_unit.y > max_y else max_y

        dimensions = {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}
        return dimensions

    def death(self):
        evopic = Evopix.objects.filter(evo_id=self.id)
        evopic.update(health=0, hype_score=0, breeding_pellet_id=None)
        land_units = LandUnit.objects.filter(evopic_id=self.id)
        land_units.update(evopic_id=None)

    def size(self):
        size = 0.
        for path in self.paths:
            size += self.paths[path].path_size()
        return size

    def color(self):
        path_rgb_vals = []
        path_sizes = []
        for path_id in self.paths:
            path = self.paths[path_id]
            if path.type == "x":
                continue
            path_sizes.append(path.path_size())
            path_rgb_vals.append(path.color())
        total_size = sum(path_sizes)
        ave_rgb = [0, 0, 0]

        for i in range(len(path_rgb_vals)):
            ave_rgb[0] += path_rgb_vals[i][0] * (path_sizes[i] / total_size)
            ave_rgb[1] += path_rgb_vals[i][1] * (path_sizes[i] / total_size)
            ave_rgb[2] += path_rgb_vals[i][2] * (path_sizes[i] / total_size)

        ave_rgb = [int(x) for x in ave_rgb]
        return ave_rgb

    def ave_points_age(self):
        point_sum = 0.
        for point in self.point_locations():
            point_sum += point[1]
        return point_sum / len(self._point_locations)

    def _database(self):
        evopic = Evopix.objects.filter(evo_id=self.id).get()
        self.health = evopic.health
        if self.health > 0:
            self.world_dimensions = self.world_xy(self.id)
            if not self.world_dimensions:  # A little house keeping, in case an evopic has no land, but still has health
                evopic.health = 0
                evopic.save()
        self.evp = evopic.evp
        self._parse_evp()
        return

    def _parse_evp(self):
        """Convert evp genome file into a dictionary of lists of its component attributes"""
        count = 1
        evp_split = self.evp.split("\n")[:-1]
        heading, paths = evp_split[0].split(":"), evp_split[1:]

        self.id = heading[0][1:]

        min_max = heading[1].split(";")
        self.min_max_points["min_x"] = float(min_max[0])
        self.min_max_points["min_y"] = float(min_max[1])
        self.min_max_points["max_x"] = float(min_max[2])
        self.min_max_points["max_y"] = float(min_max[3])

        for path in paths:
            attributes = path.split(":")
            path = Path()
            path_id = attributes[0]
            del attributes[0]
            path_type = path_id[-1:]
            path_id = int(path_id[1:-1])

            path.id = path_id
            path.type = path_type
            self.paths_order.append(path_id)

            if len(attributes) == 5:
                points, radial, linear, stops, stroke = attributes

                radial = [float(i) for i in radial.split(",")[1:]]
                path.radial = radial

                linear = [float(i) for i in linear.split(",")[1:]]
                path.linear = linear

                stops = stops.split(";")[:-1]
                for i in range(len(stops)):
                    stop = stops[i].split("~")
                    stops[i] = {"stop_id": int(stop[0][1:]), "params": stop[1].split(",")}
                    stops[i]["params"][1], stops[i]["params"][2] = [float(stops[i]["params"][1]),
                                                                    float(stops[i]["params"][2])]

                path.stops = stops

            else:
                points, stroke = attributes

            stroke = stroke.split(",")
            stroke[0], stroke[1], stroke[2] = [stroke[0][1:], float(stroke[1]), float(stroke[2])]
            path.stroke = stroke

            points = points.split("t")[1:]
            points_dict = {}
            for i in range(len(points)):
                point_id, coords = points[i].split("~")
                path.points_order.append(int(point_id))
                float_coords = []
                for j in coords.split(";")[:-1]:  # Switch 'coordinates' from string to [float, float]
                    float_coords.append([float(j.split(",")[0]), float(j.split(",")[1])])

                points_dict[int(point_id)] = float_coords

            path.points = points_dict

            self.paths[path_id] = path
            count += 1
        return

    def num_points(self, force=False):
        if self._num_points != 0 and len(self._point_locations) != 0 and not force:
            return self._num_points

        self._point_locations = []
        self._num_points = 0
        for path_id in self.paths:
            path = self.paths[path_id]
            self._num_points += len(path.points)
            for point_id in path.points:
                self._point_locations.append((path_id, point_id))

        return self._num_points

    def point_locations(self, force=False):
        # note: calling point_locations().append() actually updates self._point_locations!! Very cool.
        if force:
            self.num_points(True)

        elif len(self._point_locations) == 0:
            self.num_points()

        return self._point_locations

    def stop_locations(self):
        stop_locations = []
        for path_id in self.paths_order:
            if self.paths[path_id].type != "x":
                for i in range(len(self.paths[path_id].stops)):
                    stop_locations.append((path_id, i))
        return stop_locations

    def delete_point(self, path_id, point_id):
        if len(self.paths[path_id].points) == 1:
            self.delete_path(path_id)

        else:
            self.paths[path_id].delete_point(point_id)

        if self._num_points != 0:
            self._num_points -= 1

        if len(self._point_locations) != 0:
            index = self._point_locations.index((path_id, point_id))
            del self._point_locations[index]

    def delete_path(self, path_id):
        del self.paths[path_id]
        index = self.paths_order.index(path_id)
        del self.paths_order[index]

    def find_extremes(self):
        # arbitrarily set large min values an small max values
        min_x, min_y, max_x, max_y, min_x_seq, min_y_seg = [9999999999., 9999999999., -9999999999.,
                                                            -9999999999., [], []]

        # convert the 'control-point-control' points format of the paths into 'point-control-control-point' line
        # segments for Bézier calc
        for path_id in self.paths_order:
            path = self.paths[path_id]

            line_segments = []

            for i in range(len(path.points_order) - 1):  # Going all the way to end will give index error
                point_1 = path.points[path.points_order[i]]
                point_2 = path.points[path.points_order[i + 1]]
                line_segments.append([point_1[1], point_1[2], point_2[0], point_2[1]])

            if path.type in ["l", "r"]:  # For closed paths, link the first and last points
                point_1 = path.points[path.points_order[-1]]
                point_2 = path.points[path.points_order[0]]
                line_segments.append([point_1[1], point_1[2], point_2[0], point_1[1]])

            for seg in line_segments:
                bezier_bounds = (get_curve_bounds(seg[0][0], seg[0][1], seg[1][0], seg[1][1], seg[2][0], seg[2][1],
                                                  seg[3][0], seg[3][1]))

                min_x = bezier_bounds['left'] if bezier_bounds['left'] < min_x else min_x
                min_y = bezier_bounds['top'] if bezier_bounds['top'] < min_y else min_y
                max_x = bezier_bounds['right'] if bezier_bounds['right'] > max_x else max_x
                max_y = bezier_bounds['bottom'] if bezier_bounds['bottom'] > max_y else max_y

        self.min_max_points = {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}

    def reconstruct_evp(self):
        """Reconstruct evp genome from self.paths attribs"""
        new_evp = "e%s:%s;%s;%s;%s\n" % (self.id, self.min_max_points["min_x"], self.min_max_points["min_y"],
                                         self.min_max_points["max_x"], self.min_max_points["max_y"])
        for path_id in self.paths_order:
            path = self.paths[path_id]
            new_evp += "p%s%s:" % (path.id, path.type)
            for point_id in path.points_order:
                coords = path.points[point_id]
                new_evp += "t%s~%s,%s;%s,%s;%s,%s;" % (point_id, coords[0][0], coords[0][1], coords[1][0],
                                                       coords[1][1], coords[2][0], coords[2][1])

            if path.type in ["r", "l"]:  # skip if the path is not closed
                new_evp += ":r,%s,%s,%s,%s,%s" % tuple(path.radial)
                new_evp += ":l,%s,%s,%s,%s:" % tuple(path.linear)

                for stop in path.stops:
                    params = stop["params"]
                    new_evp += "o%s~%s,%s,%s;" % (stop["stop_id"], params[0], params[1], params[2])

            new_evp += ":s%s,%s,%s\n" % tuple(path.stroke)
        self.evp = new_evp
        return

    def svg_out(self, scale=1, bounding_box=False):  # Bbox is tupel (width, height)
        """
        Uses the info in self.paths to create an SVG file. Returned as a string.
        If bounding box is used, the svg will be centered, and compressed if too big.
        """
        shift_x, shift_y = 0., 0.
        if bounding_box:
            box_width, box_height = bounding_box
            evo_width = (self.min_max_points["max_x"] - self.min_max_points["min_x"]) * scale
            evo_height = (self.min_max_points["max_y"] - self.min_max_points["min_y"]) * scale

            # Executes when the evopic is wider than bounding box and by a greater extent than height
            if evo_width > box_width and box_width - evo_width < box_height - evo_height:
                scale = 1. - (evo_width - box_width) / evo_width
                shift_y -= round((box_height - evo_height) / 2, 6)

            # Execute if evopic height is greater than bounding box
            elif evo_height > box_height:
                scale = 1. - (evo_width - box_width) / evo_width
                shift_x -= round((box_width - evo_width) / 2, 6)

            # Ideally, this is where things will usually shake out. It's better if we don't make a habit of scaling
            # to a bounding box.
            else:
                shift_y -= round((box_height - evo_height) / 2, 6)
                shift_x -= round((box_width - evo_width) / 2, 6)
        else:
            box_width = round(self.min_max_points["max_x"] * scale, 6)
            box_height = round(self.min_max_points["max_y"] * scale, 6)

        # header info
        svg = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>"

        svg += "<svg xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' " \
               "xmlns:xlink='http://www.w3.org/1999/xlink' version='1.0' width='%spx' height='%spx' id='svg%s'>\n" % \
               (box_width, box_height, self.id)

        # gradient/color info
        svg += "<defs>\n"
        for i in self.paths_order:
            path = self.paths[i]
            if path.type == 'x':
                continue

            if path.type == 'l':
                x1, y1, x2, y2 = path.linear
                svg += "\t<linearGradient id='linearGradient%s' x1='%s' y1='%s' x2='%s' y2='%s'>\n" % (path.id, x1, y1,
                                                                                                       x2, y2)
                for j in path.stops:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</linearGradient>\n"

            if path.type == 'r':
                cx, cy, fx, fy, r = path.radial
                svg += "\t<radialGradient id='radialGradient%s' cx='%s' cy='%s' fx='%s' fy='%s' r='%s'>\n" \
                       % (path.id, cx, cy, fx, fy, r)

                for j in path.stops:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</radialGradient>\n"

        svg += "</defs>\n"

        # paths
        for i in self.paths_order:
            path = self.paths[i]
            grad_type = "linear" if path.type == "l" else "radial"
            color, width, opacity = path.stroke
            width = round(width * scale, 6)

            points_string = "M "

            if path.type == 'x':  # closed paths first
                count = 0
                for point_id in path.points_order:
                    point = path.points[point_id]
                    # zero out and apply scaling factor
                    for j in range(3):
                        point[j][0] = round((point[j][0] - self.min_max_points["min_x"]) * scale, 6) - shift_x
                        point[j][1] = round((point[j][1] - self.min_max_points["min_y"]) * scale, 6) - shift_y

                    if count == 0:
                        points_string += "%s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    elif count == len(path.points) - 1:
                        points_string += " %s %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'),
                                                          str(point[2]).strip('[]'))

                    count += 1

                strings = (path.id, points_string, color, width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:none;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" \
                       % strings

            else:
                count = 0
                start_point = ("", "")
                for point_id in path.points_order:
                    point = path.points[point_id]
                    for j in range(3):
                        point[j][0] = round((point[j][0] - self.min_max_points["min_x"]) * scale, 6) - shift_x
                        point[j][1] = round((point[j][1] - self.min_max_points["min_y"]) * scale, 6) - shift_y

                    if count == 0:  # This is always true on the first pass through the loop, then always false
                        start_point = (str(point[0]).strip('[]'), str(point[1]).strip('[]'))
                        points_string += "%s C %s" % (str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'),
                                                          str(point[2]).strip('[]'))

                    count += 1

                points_string += " %s %s z" % start_point
                strings = (path.id, points_string, grad_type, path.id, color, width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:url(#%sGradient%s);fill-rule:evenodd;stroke:#%s;" \
                       "stroke-width:%s;stroke-opacity:%s' />\n" % strings
        svg += "</svg>"
        return svg

    def save(self, location='local', parents=(0, 0)):
        if location not in ['local', 'db']:
            sys.exit("%s is not a valid save location. Choose 'local' or 'db'" % location)

        if location == 'local':
            max_stop_id = 0
            for path_id in self.paths_order:
                path = self.paths[path_id]
                for stop in path.stops:
                    if stop["stop_id"] > max_stop_id:
                        max_stop_id = stop["stop_id"]

                if path_id < 0:
                    new_id = max(self.paths_order) + 1
                    self.paths[new_id] = self.paths[path_id]
                    self.paths[new_id].id = new_id
                    del(self.paths[path_id])
                    old_id_index = self.paths_order.index(path_id)
                    self.paths_order[old_id_index] = new_id
                    self.point_locations(force=True)

            for path_id in self.paths_order:
                path = self.paths[path_id]
                for i in range(len(path.points_order)):
                    point_id = path.points_order[i]
                    if point_id < 0:
                        new_id = max(path.points_order) + 1
                        self.paths[path_id].points_order[i] = new_id
                        self.paths[path_id].points[new_id] = self.paths[path_id].points[point_id]
                        del(self.paths[path_id].points[point_id])
                        self.point_locations(force=True)

                if path.type != "x":
                    for i in range(len(path.stops)):
                        if path.stops[i]["stop_id"] < 0:
                            self.paths[path_id].stops[i]["stop_id"] = max_stop_id + 1
                            max_stop_id += 1
            self.reconstruct_evp()

        else:  # send to database
            if not parents or 0 in parents:
                sys.exit("Error: you need to provide parent IDs if you want to save to database")

            new_evopic = Evopix(parent1=parents[0], parent2=parents[1], hype_score=0, health=1)
            new_evopic.save()
            self.id = new_evopic.evo_id
            for path_id in self.paths_order:
                if path_id < 0:
                    new_path = Paths(parent_path=path_id*-1, parent_evopic_id=new_evopic.evo_id)
                    new_path.save()
                    new_id = new_path.path_id
                    self.paths[new_id] = self.paths[path_id]
                    self.paths[new_id].id = new_id
                    del(self.paths[path_id])
                    old_id_index = self.paths_order.index(path_id)
                    self.paths_order[old_id_index] = new_id
                    self.point_locations(force=True)

            for path_id in self.paths_order:
                path = self.paths[path_id]
                for i in range(len(path.points_order)):
                    point_id = path.points_order[i]
                    if point_id < 0:
                        new_point = Points(parent_point=point_id * -1, parent_path_id=path_id,
                                           parent_evopic_id=new_evopic.evo_id)
                        new_point.save()
                        new_id = new_point.point_id
                        self.paths[path_id].points_order[i] = new_id
                        self.paths[path_id].points[new_id] = self.paths[path_id].points[point_id]
                        del(self.paths[path_id].points[point_id])
                        self.point_locations(force=True)

                if path.type != "x":
                    for i in range(len(path.stops)):
                        if path.stops[i]["stop_id"] < 0:
                            new_stop = Stops(parent_stop=path.stops[i]["stop_id"] * -1, parent_path_id=path_id,
                                             parent_evopic_id=new_evopic.evo_id)
                            new_stop.save()
                            self.paths[path_id].stops[i]["stop_id"] = new_stop.stop_id

            self.reconstruct_evp()
            new_evopic.evp = self.evp
            new_evopic.save()


class Path():
    def __init__(self):
        self.id = int()
        self.type = str()
        self.radial = []
        self.linear = []
        self.stops = []
        self.points = {}
        self.points_order = []
        self.stroke = []

    def __str__(self):
        return("id: %s\ntype: %s\npoints order: %s\npoints: %s\n" %
               (self.id, self.type, self.points_order, self.points))

    def color(self):  # return the rgb hex value of the path
        rgb = [0, 0, 0]
        for stop in self.stops:
            color = stop["params"][0]
            components = [int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)]
            rgb[0] += components[0]
            rgb[1] += components[1]
            rgb[2] += components[2]

        return [int(x / len(self.stops)) for x in rgb]

    def find_area(self):  # Input is an individual path from Evopic.paths
        """
        Modified from http://www.arachnoid.com/area_irregular_polygon/index.html
        Calculates the area of an irregular polygon using the sum of the cross products of each neighboring pair of
        coords. It's super nice, because it scales at N.
        """
        array = []
        for point_id in self.points_order:
            array.append(self.points[point_id][1])

        area = 0
        ox, oy = array[-1]  # set the 'first' point as the same as the last point, to close the path
        for x, y in array:
            try:
                area += (x * oy - y * ox)
            except TypeError:
                print(x, oy, y, ox)
                sys.exit("Error: Evopic.find_area()")
            ox, oy = x, y
        return abs(area / 2)

    def find_perimeter(self):  # Input is an individual path from Evopic.paths
        length = 0.
        ox, oy = self.points[self.points_order[0]][1]
        for point_id in self.points_order[1:]:
            point = self.points[point_id]
            length += LineSeg([ox, oy], point[1]).length()
            ox, oy = point[1]

        if self.type in ["r", "l"]:
            length += LineSeg([ox, oy], self.points[self.points_order[0]][1]).length()

        return length

    def path_size(self):
        """
        Returns a value that is comparable between closed and open paths, and smooths out the possible issues in closed
        paths relating to area vs perimeter measurement (ie, it's possible to have a lot of perimeter with very little
        area)
        """
        # For closed paths, the size of the path is average(sqrt(area) * 4, perimeter)
        if self.type in ["r", "l"]:
            size = (self.find_area() ** 0.5 + self.find_perimeter()) / 2.

        # For open paths, the size is just path length
        else:
            size = self.find_perimeter()

        size += 1.  # When a path only has a single point, its size is 0. This just makes sure there is always some size

        return size

    def delete_point(self, point_id):
        del self.points[point_id]
        point_index = self.points_order.index(point_id)
        del self.points_order[point_index]


def get_curve_bounds(x0, y0, x1, y1, x2, y2, x3, y3):
    """Calculates the extreme points of a cubic Bézier curve
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
        sqrtb2ac = b2ac ** 0.5
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
def run():
    from resources.Evo import LineSeg
    bob = Evopic(Evopix.objects.filter(evo_id=1).get().evp)
    #bob.reconstruct_evp()
    bob = mutation.mutate(bob)
    bob.save(location='db', parents=(1, 2))
    print(bob.id)




