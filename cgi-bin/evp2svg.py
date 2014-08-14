#! /usr/bin/python
class Evopic():
    def __init__(self, evp):
        self.evp = evp
        self.paths = False
        self._parse_evp()

    def _parse_evp(self):  # Convert evp genome file into a dictionary of lists of its component parts
        self.paths = self.evp.split("\n")
        count = 0
        for path in self.paths:
            attributes = path.split(":")
            if len(attributes) == 6:
                path_id, points, radial, linear, stops, stroke = attributes
                stops = self.read_stops(stops)
                stroke = stroke.split(",")
                radial = radial.split(",")
                linear = linear.split(",")
                self.paths[count] = {"path_id": path_id[1:], "points": points, "radial": radial[1:],
                                     "linear": linear[1:], "stops": stops, "stroke": stroke}

            else:
                path_id, points, stroke = attributes
                stroke = stroke.split(",")
                self.paths[count] = {"path_id": path_id[1:], "points": points, "stroke": stroke}

            self.paths[count]["points"] = self.read_points(self.paths[count]["points"])
            count += 1

    def reconstruct_evp(self):
        x = 1

    def read_points(self, points_string):
        points = points_string.split("t")[1:]
        count = 0
        for point in points:
            point_id, coords = point.split("~")
            float_coords = []
            for i in coords.split(";")[:-1]:  # Get the coordinates for each point into a float, instead of a string
                float_coords.append([float(i.split(",")[0]), float(i.split(",")[1])])

            points[count] = {"point_id": point_id, "coords": float_coords}
            count += 1

        return points

    def read_stops(self, stops_string):
        stops = stops_string.split(";")
        count = 0
        for stop in stops:
            stop = stop.split("~")
            stops[count] = {"stop_id": stop[0][1:], "params": stop[1].split(",")}
            count += 1
        return stops

    def loop_paths(self, attrib):
        output = []
        for path in self.paths:
            try:
                output += [path[attrib]]
            except KeyError:
                output += [False]
        return output

    def svg_out(self, scale=100):
        path_ids = self.loop_paths('path_id')
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
            x1, y1, x2, y2 = linears[i]
            svg += "\t<linearGradient id='linearGradient%s' x1='%s' y1='%s' x2='%s' y2='%s'>\n" % (path_ids[i][:-1], x1, y1, x2, y2)
            for j in stops[i]:
                color, opacity, offset = j['params']
                svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
            svg += "\t</linearGradient>\n"

            cx, cy, fx, fy, r = radials[i]
            svg += "\t<radialGradient id='radialGradient%s' cx='%s' cy='%s' fx='%s' fy='%s' r='%s'>\n" % (path_ids[i][:-1], cx, cy, fx, fy, r)
            for j in stops[i]:
                color, opacity, offset = j['params']
                svg += "\t\t<stop stop-color='#%s' stop-opacity='%s' offset='%s' />\n" % (color, opacity, offset)
            svg += "\t</radialGradient>\n"

        svg += "</defs>\n"

        #paths
        for i in range(len(path_ids)):
            path_id = path_ids[i][:-1]
            grad_type = "linear" if path_ids[i][-1:] == "l" else "radial"
            color, width, opacity = strokes[i]

            points_string = "M "

            if not linears[i]:
                count = 0
                for point in points[i]:
                    point = point['coords']
                    if count == 0:
                        points_string += "%s C %s" % (point[0], point[1])

                    elif count == len(points[i])-1:
                        points_string += " %s %s" % (point[0], point[1])

                    else:
                        points_string += " %s %s C %s" % (point[0], point[1], point[2])

                    count += 1

                strings = (path_id, points_string, color[1:], width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:none;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings

            else:
                count = 0
                for point in points[i]:
                    point = point['coords']
                    if count == 0:
                        start_point = (point[0], point[1])
                        points_string += "%s C %s" % (point[1], point[2])

                    else:
                        points_string += " %s %s C %s" % (point[0], point[1], point[2])

                    count += 1

                points_string += " %s %s z" % start_point
                strings = (path_id, points_string, grad_type, path_id, color[1:], width, opacity)
                svg += "<path id='path%s' d='%s' style='fill:url(#%sGradient%s);fill-rule:evenodd;stroke:#%s;stroke-width:%s;stroke-opacity:%s' />\n" % strings
        svg += "</svg>"
        return svg


#--------------------------------------------------------#

if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        #print bob.evp
        print(breed.zero_evp(bob.evp))
        #print(bob.svg_out())
#print bob.paths[0]["points"]

