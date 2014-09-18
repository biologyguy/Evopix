#! /usr/bin/python3
import sys


class Evopic():
    def __init__(self, evp):
        self.evp = evp
        self.paths = {}
        self.paths_order = []
        self._parse_evp()
        self._num_points = False

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
        if self._num_points:
            return self._num_points

        output = 0
        for path_id in self.paths:
            output += len(self.paths[path_id].points)

        self._num_points = output
        return output

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

                    elif count == len(path.points)-1:
                        points_string += " %s %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    count += 1

                strings = (path.id, points_string, color, width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:none;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings

            else:
                count = 0
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

    @staticmethod
    def line_length(point_a, point_b):  # implement Pythagorean theorem
        length = (abs(point_a[0] - point_b[0])**2 + abs(point_a[1] - point_b[1])**2)**0.5
        return length

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
            area += (x * oy - y * ox)
            ox, oy = x, y
        return abs(area/2)

    def find_perimeter(self):  # Input is an individual path from Evopic.paths
        length = 0.
        ox, oy = self.points[self.points_order[0]][1]
        for point_id in self.points_order[1:]:
            point = self.points[point_id]
            length += self.line_length([ox, oy], point[1])
            ox, oy = point[1]

        if self.type in ["r", "l"]:
            length += self.line_length([ox, oy], self.points[self.points_order[0]][1])

        return length

    def path_size(self):
        """
        Returns a value that is comparable between closed and open paths, and smooths out the possible issues in closed
        paths relating to area vs perimeter measurement (ie, it's possible to have a lot of perimeter with very little area)
        """
        # For closed paths, the size of the path is average(sqrt(area) * 4, perimeter)
        if self.type in ["r", "l"]:
            size = (self.find_area() ** 0.5 + self.find_perimeter())/2.

        # For open paths, the size is just path length
        else:
            size = self.find_perimeter()

        return size


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    path = "../genomes/bubba"
    with open("%s.evp" % path, "r") as infile:
        bob = Evopic(infile.read())
    #bob.reconstruct_evp()
    print(bob.paths[5].path_size())
    #with open("../genomes/test.svg", "w") as ofile:
    #    ofile.write(bob.svg_out())
    sys.exit()
    print("Attribute\tValue(s)")
    for attrib in bob.paths[1]:
        print("%s:\t%s" % (attrib, bob.paths[1][attrib]))


