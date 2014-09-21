#! /usr/bin/python3
import sys


class Evopic():
    def __init__(self, evp):
        self.evp = evp
        self.paths = {}
        self.paths_order = []
        self._parse_evp()
        self._num_points = 0
        self._point_locations = []

    def _parse_evp(self):
        """Convert evp genome file into a dictionary of lists of its component attributes"""
        count = 1
        paths = self.evp.split("\n")[:-1]
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
                    stops[i]["params"][1], stops[i]["params"][2] = [float(stops[i]["params"][1]), float(stops[i]["params"][2])]

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

    def num_points(self):
        if self._num_points != 0 and len(self._point_locations) != 0:
            return self._num_points

        for path_id in self.paths:
            path = self.paths[path_id]
            self._num_points += len(path.points)
            for point_id in path.points:
                self._point_locations.append((path_id, point_id))

        return self._num_points

    def point_locations(self):
        if len(self._point_locations) == 0:
            self.num_points()
        return self._point_locations

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

    def insert_point(self, path_id, point_id):
        x = 1

    def reconstruct_evp(self):
        """Reconstruct evp genome from self.paths attribs. Used by zero_evp() in breeding.py."""
        new_evp = ""
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

    def svg_out(self, scale=100):  # need to implement a scaling factor, so full sized vs. thumbnail versions can be made
        """Uses the info in self.paths to create an SVG file. Returned as a string."""

        #header info
        svg = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>\n"

        svg += "<svg xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' " \
               "xmlns:xlink='http://www.w3.org/1999/xlink' version='1.0' width='582' height='582' id='svg2232'>\n"

        #gradient/color info
        svg += "<defs>\n"
        for i in self.paths_order:
            path = self.paths[i]
            if path.type == 'x':
                continue

            if path.type == 'l':
                x1, y1, x2, y2 = path.linear
                svg += "\t<linearGradient id='linearGradient%s' x1='%s' y1='%s' x2='%s' y2='%s'>\n" % (path.id, x1, y1, x2, y2)
                for j in path.stops:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</linearGradient>\n"

            if path.type == 'r':
                cx, cy, fx, fy, r = path.radial
                svg += "\t<radialGradient id='radialGradient%s' cx='%s' cy='%s' fx='%s' fy='%s' r='%s'>\n" % (path.id, cx, cy, fx, fy, r)
                for j in path.stops:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</radialGradient>\n"

        svg += "</defs>\n"

        #paths
        for i in self.paths_order:
            path = self.paths[i]
            grad_type = "linear" if path.type == "l" else "radial"
            color, width, opacity = path.stroke

            points_string = "M "

            if path.type == 'x':  # closed paths first
                count = 0
                for point_id in path.points_order:
                    point = path.points[point_id]
                    if count == 0:
                        points_string += "%s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    elif count == len(path.points) - 1:
                        points_string += " %s %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    count += 1

                strings = (path.id, points_string, color, width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:none;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings

            else:
                count = 0
                start_point = ("", "")
                for point_id in path.points_order:
                    point = path.points[point_id]
                    if count == 0:  # This is always true on the first pass through the loop, then always false
                        start_point = (str(point[0]).strip('[]'), str(point[1]).strip('[]'))
                        points_string += "%s C %s" % (str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    count += 1

                points_string += " %s %s z" % start_point
                strings = (path.id, points_string, grad_type, path.id, color, width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:url(#%sGradient%s);fill-rule:evenodd;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings
        svg += "</svg>"
        return svg


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

    def find_area(self):  # Input is an individual path from Evopic.paths
        """
        Modified from http://www.arachnoid.com/area_irregular_polygon/index.html
        Calculates the area of an irregular polygon using the sum of the cross products of each neighboring pair of coords.
        It's super nice, because it scales at N.
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
            length += Line([ox, oy], point[1]).length()
            ox, oy = point[1]

        if self.type in ["r", "l"]:
            length += Line([ox, oy], self.points[self.points_order[0]][1]).length()

        return length

    def path_size(self):
        """
        Returns a value that is comparable between closed and open paths, and smooths out the possible issues in closed
        paths relating to area vs perimeter measurement (ie, it's possible to have a lot of perimeter with very little area)
        """
        # For closed paths, the size of the path is average(sqrt(area) * 4, perimeter)
        if self.type in ["r", "l"]:
            size = (self.find_area() ** 0.5 + self.find_perimeter()) / 2.

        # For open paths, the size is just path length
        else:
            size = self.find_perimeter()

        return size

    def delete_point(self, point_id):
        del self.points[point_id]
        index = self.points_order.index(point_id)
        del self.points_order[index]


class Line():
    def __init__(self, point_a, point_b):
        self.x1, self.y1, self.x2, self.y2 = float(point_a[0]), float(point_a[1]), float(point_b[0]), float(point_b[1])

    def length(self):
        return (abs(self.x1 - self.x2) ** 2 + abs(self.y1 - self.y2) ** 2) ** 0.5

    def slope(self):
        return (self.y2 - self.y1) / (self.x2 - self.x1)

    def intercept(self):
        return self.y2 - (self.slope() * self.x2)

#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    evo_path = "../genomes/bubba"
    with open("%s.evp" % evo_path, "r") as infile:
        bob = Evopic(infile.read())
    #bob.reconstruct_evp()
    print(bob.num_points())
    #with open("../genomes/test.svg", "w") as ofile:
    #    ofile.write(bob.svg_out())
    sys.exit()
    print("Attribute\tValue(s)")
    for attrib in bob.paths[1]:
        print("%s:\t%s" % (attrib, bob.paths[1][attrib]))


