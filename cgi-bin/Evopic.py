#! /usr/bin/python3
import sys


class Evopic():
    def __init__(self, evp):
        self.evp = evp
        self.paths = {}
        self.paths_z_pos = []
        self._parse_evp()

    def _parse_evp(self):
        """Convert evp genome file into a dictionary of lists of its component attributes"""
        count = 1
        for path in self.evp.split("\n")[:-1]:
            attributes = path.split(":")
            path_id = attributes[0]
            del attributes[0]
            path_type = path_id[-1:]
            path_id = int(path_id[1:-1])

            self.paths[path_id] = {"path_id": path_id, "type": path_type}
            self.paths_z_pos.append(path_id)

            if len(attributes) == 5:
                points, radial, linear, stops, stroke = attributes

                radial = [float(i) for i in radial.split(",")[1:]]
                self.paths[path_id]["radial"] = radial

                linear = [float(i) for i in linear.split(",")[1:]]
                self.paths[path_id]["linear"] = linear

                stops = stops.split(";")[:-1]
                for i in range(len(stops)):
                    stop = stops[i].split("~")
                    stops[i] = {"stop_id": int(stop[0][1:]), "params": stop[1].split(",")}
                    stops[i]["params"][1], stops[i]["params"][2] = [float(stops[i]["params"][1]), float(stops[i]["params"][2])]

                self.paths[path_id]["stops"] = stops

            else:
                points, stroke = attributes

            stroke = stroke.split(",")
            stroke[0], stroke[1], stroke[2] = [stroke[0][1:], float(stroke[1]), float(stroke[2])]
            self.paths[path_id]["stroke"] = stroke

            points = points.split("t")[1:]
            for i in range(len(points)):
                point_id, coords = points[i].split("~")
                float_coords = []
                for j in coords.split(";")[:-1]:  # Switch 'coordinates' from string to [float, float]
                    float_coords.append([float(j.split(",")[0]), float(j.split(",")[1])])

                points[i] = {"point_id": int(point_id), "coords": float_coords}

            self.paths[path_id]["points"] = points
            count += 1
        return

    def loop_paths(self, attrib):
        """Pushes the values for a single attribute from every path into a list"""
        output = []
        for path_id in self.paths_z_pos:
            path = self.paths[path_id]
            try:
                output += [path[attrib]]
            except KeyError:  # This is a hack for skipping linears, radials, and stops for non-closed paths
                output += [False]
        return output

    def reconstruct_evp(self):
        """Reconstruct evp genome from self.paths attribs. Used by zero_evp() in breeding.py."""
        new_evp = ""
        for path_id in self.paths_z_pos:
            path = self.paths[path_id]
            new_evp += "p%s%s:" % (path["path_id"], path["type"])
            for point in path["points"]:
                coords = point["coords"]
                new_evp += "t%s~%s,%s;%s,%s;%s,%s;" % (point["point_id"], coords[0][0], coords[0][1], coords[1][0],
                                                       coords[1][1], coords[2][0], coords[2][1])

            if path["type"] in ["r", "l"]:  # skip if the path is not closed
                new_evp += ":r,%s,%s,%s,%s,%s" % tuple(path["radial"])
                new_evp += ":l,%s,%s,%s,%s:" % tuple(path["linear"])

                for stop in path["stops"]:
                    params = stop["params"]
                    new_evp += "o%s~%s,%s,%s;" % (stop["stop_id"], params[0], params[1], params[2])

            new_evp += ":%s,%s,%s\n" % tuple(path["stroke"])
        self.evp = new_evp
        return

    def svg_out(self, scale=100):  # need to implement a scaling factor, so full sized vs. thumbnail versions can be made
        """Uses the info in self.paths to create an SVG file. Returned as a string."""
        path_ids = self.loop_paths('path_id')
        path_type = self.loop_paths('type')
        points = self.loop_paths('points')
        linears = self.loop_paths('linear')
        radials = self.loop_paths('radial')
        stops = self.loop_paths('stops')
        strokes = self.loop_paths('stroke')

        #header info
        svg = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>\n"

        svg += "<svg xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' " \
               "xmlns:xlink='http://www.w3.org/1999/xlink' version='1.0' width='582' height='582' id='svg2232'>\n"

        #gradient/color info
        svg += "<defs>\n"
        for i in range(len(linears)):
            if not linears[i]:
                continue

            if path_type[i] == 'l':
                x1, y1, x2, y2 = linears[i]
                svg += "\t<linearGradient id='linearGradient%s' x1='%s' y1='%s' x2='%s' y2='%s'>\n" % (path_ids[i], x1, y1, x2, y2)
                for j in stops[i]:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</linearGradient>\n"

            if path_type[i] == 'r':
                cx, cy, fx, fy, r = radials[i]
                svg += "\t<radialGradient id='radialGradient%s' cx='%s' cy='%s' fx='%s' fy='%s' r='%s'>\n" % (path_ids[i], cx, cy, fx, fy, r)
                for j in stops[i]:
                    color, opacity, offset = j['params']
                    svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
                svg += "\t</radialGradient>\n"

        svg += "</defs>\n"

        #paths
        for i in range(len(path_ids)):
            path_id = path_ids[i]
            grad_type = "linear" if path_type[i] == "l" else "radial"
            color, width, opacity = strokes[i]

            points_string = "M "

            if not linears[i]:
                count = 0
                for point in points[i]:
                    point = point['coords']
                    if count == 0:
                        points_string += "%s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    elif count == len(points[i])-1:
                        points_string += " %s %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    count += 1

                strings = (path_id, points_string, color[1:], width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:none;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings

            else:
                count = 0
                for point in points[i]:
                    point = point['coords']
                    if count == 0:  # This is always true on the first pass through the loop, then always false
                        start_point = (str(point[0]).strip('[]'), str(point[1]).strip('[]'))
                        points_string += "%s C %s" % (str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    else:
                        points_string += " %s %s C %s" % (str(point[0]).strip('[]'), str(point[1]).strip('[]'), str(point[2]).strip('[]'))

                    count += 1

                points_string += " %s %s z" % start_point
                strings = (path_id, points_string, grad_type, path_id, color[1:], width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:url(#%sGradient%s);fill-rule:evenodd;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings
        svg += "</svg>"
        return svg


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    path = "../genomes/bubba"
    with open("%s.evp" % path, "r") as infile:
        bob = Evopic(infile.read())

    print(bob.svg_out())
    sys.exit()
    print("Attribute\tValue(s)")
    for attrib in bob.paths[1]:
        print("%s:\t%s" % (attrib, bob.paths[1][attrib]))


