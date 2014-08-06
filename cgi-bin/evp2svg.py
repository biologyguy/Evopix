#! /usr/bin/python
import sys

class Evopic():
    def __init__(self, evp):
        self.evp = evp
        self.paths = False 

        self._parse_evp()
        
        #min_x, min_y = [9999999999.9, 9999999999.9]  # arbitrarily set large min values for self.zero_paths()
        self.zeroed_paths = False  # The raw evp genome is free to roam around cartesian space. When it's zeroed out \
                                   # with self.zero_paths(), this gets set to True

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

    def read_points(self, points_string):
        points = points_string.split("t")[1:]
        count = 0
        for point in points:
            point_id, coords = point.split("~")
            coords = coords.split(";")[:-1]
            points[count] = {"point_id": point_id, "coords": coords}
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
        #if not self.zeroed_paths:
        #    print "Error: object's zeroed_path data has not been set"
        #    return False

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

    def find_mid(self, pt1, pt2):
        mid_x = abs(pt1[0]-pt2[0])/2 + min(pt1[0], pt2[0])
        mid_y = abs(pt1[1]-pt2[1])/2 + min(pt1[1], pt2[1])
        return [mid_x, mid_y]


    def zero_evp(self):  #This is not done yet
        min_x, min_y = [9999999999.9, 9999999999.9]  # arbitrarily set large min values for self.zero_paths()

        # convert the 'control-point-control' points format of the paths into 'point-control-control-point' line segments for bezier calc
        line_segments = []
        points = self.loop_paths("points")
        path_ids = self.loop_paths("path_id")

        count = 0
        for point in points:
            line_segments = []
            if not path_ids[count][-1] == "x":
                for i in range(len(point)):
                    if i+1 == len(point):
                        line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[0]['coords'][0], point[0]['coords'][1]])
                    else:
                        line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[i+1]['coords'][0], point[i+1]['coords'][1]])
            else:
                for i in range(len(point)):
                    if i+1 == len(point):
                        continue
                    else:
                        line_segments.append([point[i]['coords'][1], point[i]['coords'][2], point[i+1]['coords'][0], point[i+1]['coords'][1]])

            for seg in line_segments:
                for i in range(len(seg)):
                    seg[i] = seg[i].split(",")
                    seg[i] = [float(seg[i][0]), float(seg[i][1])]

                mid_pt1 = self.find_mid(seg[0], seg[1])
                mid_pt2 = self.find_mid(seg[2], seg[3])
                mid_pt3 = self.find_mid(seg[1], seg[2])

                mid_pt4 = self.find_mid(mid_pt1, mid_pt3)
                mid_pt5 = self.find_mid(mid_pt2, mid_pt3)

                mid_pt6 = self.find_mid(mid_pt4, mid_pt5)

                if min_x > mid_pt6[0]:
                    min_x = mid_pt6[0]

                if min_x > seg[0][0]:
                    min_x = seg[0][0]

                if min_x > seg[3][0]:
                    min_x = seg[3][0]

                if min_y > mid_pt6[1]:
                    min_y = mid_pt6[1]

                if min_y > seg[0][1]:
                    min_y = seg[0][1]

                if min_y > seg[3][1]:
                    min_y = seg[3][1]

            count += 1

        print min_x
        print min_y
        return


#--------------------------------------------------------#

with open("../genomes/bob.evp", "r") as infile:
    bob = Evopic(infile.read())
    #print bob.evp
    #print breed.zero_evp(bob.evp)
    print bob.svg_out()
#print bob.paths[0]["points"]

