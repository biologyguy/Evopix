#! /usr/bin/python
try:
    from Evopic import *
except ImportError:
    from resources.Evopic import *


def breed(evp1, evp2):
    """Notes:-The original evp file (i.e., not zeroed) needs to be used for breeding. Store the zeroed evp for printing.
             -moderate to extreme values in offset and radius totally break the fill of a gradient in some browsers
             -Pass in parents as evopic objects.
    """
    return "A couple of Evopics just made a baby.\n"


def zero_evp(evp):
    """New Evopix are able to wander around Cartesian space, which means they would start to wander off the canvas
    pretty quickly if we print the SVG true to their actual genome coords. Instead, create a separate evp file that
    finds the bounding box of the image and positions it close to 0,0. It's important to still breed from the original
    non-zeroed evp though, because a mutation on the extreme left or top of the image will result in new values for all
    coords, making it look like much more divergence between parent and offspring than there really is."""
    evopic = Evopic(evp)
    evopic.find_extremes()

    #adjust min x,y so they are not perfectly 0. Giving a little bit of padding looks nicer.
    for i in evopic.min_max_points:
        evopic.min_max_points[i] -= 3

    for path_id in evopic.paths_order:
        path = evopic.paths[path_id]
        for point_id in path.points_order:
            coords_count = 0
            for coords in path.points[point_id]:
                coords[0] = coords[0] - evopic.min_max_points["min_x"]
                coords[1] = coords[1] - evopic.min_max_points["min_y"]

                path.points[point_id][coords_count] = [round(coords[0], 4), round(coords[1], 4)]
                coords_count += 1

    evopic.find_extremes()  # run a second time to update min_max_points to the new values
                            # (This could probably be updated directly without the function call)
    evopic.reconstruct_evp()
    return evopic.evp


#-------------------------Sandbox-------------------------------#
if __name__ == '__main__':
    with open("../genomes/bob.evp", "r") as infile:
        bob = Evopic(infile.read())
        print(bob.paths[1].points_order)
    with open("../genomes/sue.evp", "r") as infile:
        sue = Evopic(infile.read())
    print("HELLO!")