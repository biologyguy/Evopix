import sys


class LineSeg():
    def __init__(self, point_a, point_b):
        self.x1, self.y1, self.x2, self.y2 = float(point_a[0]), float(point_a[1]), float(point_b[0]), float(point_b[1])

    def length(self):
        return (abs(self.x1 - self.x2) ** 2 + abs(self.y1 - self.y2) ** 2) ** 0.5

    def slope(self):
        if self.x2 == self.x1:  # this prevents divide-by-zero error when slope is infinity
            return sys.maxsize
        return (self.y2 - self.y1) / (self.x2 - self.x1)

    def intercept(self):
        return self.y2 - (self.slope() * self.x2)