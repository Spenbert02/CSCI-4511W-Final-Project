import numpy as np
from Point import Point


class Line:
    """
    Line class. makes stuff in the Tile class easier and more concise
    """
    def __init__(self, p0, p1):
        if p0 == p1:
            raise ValueError("line initialization points must be distinct")

        self.p0 = p0
        self.p1 = p1
        self.traversed = False
        self.test = False  # FOR TESTING PURPOSES
    
        if self.p0.x == self.p1.x:  # vertical line has slope None
            self.slope = None
        else:
            self.slope = (self.p0.y - self.p1.y) / (self.p0.x - self.p1.x)
    
    def f(self, x):
        """
        line description as a function of x
        """
        if self.slope is None:  # vertical line, return None
            return None
        else:
            return self.p0.y - (self.slope * (self.p0.x - x))
    
    def length(self):
        return Point.distance(self.p0, self.p1)

    def xList(self):
        return (self.p0.x, self.p1.x)
    
    def yList(self):
        return (self.p0.y, self.p1.y)

    def translateOrthogonal(self, offset):
        """
        given an offset distance, orthogonally translate the line. If offset > 0, moves the line generally to the right. If offset < 0,
        moves the line generally to the left. If the line is horizontal, offset > 0 moves it up and offset < 0 moves it down.
        """
        if self.slope == 0:  # if line is horizontal. easy, just offset y's
            self.p0.y += offset
            self.p1.y += offset
        elif self.slope is None:  # if line is vertical. also easy, just offset x's
            self.p0.x += offset
            self.p1.x += offset
        else:
            angle = np.arctan2(self.slope, 1)
            angle += (np.pi if angle < 0 else 0)
            offset_vector = (offset * np.sin(angle), -offset * np.cos(angle))
            self.p0.x += offset_vector[0]
            self.p1.x += offset_vector[0]
            self.p0.y += offset_vector[1]
            self.p1.y += offset_vector[1]

    def orthogonalDistance(self, point):
        """
        return orthogonal distance from the infinite line represented by this line segment to a given point
        """
        if self.slope is None:
            return np.abs(point.x - self.p0.x)  # x-distance
        elif np.abs(self.slope) < 10**(-5):
            return np.abs(point.y - self.p0.y)  # y-distance
        
        orth_slope = -(1 / self.slope)
        orth_line = Line(point, Point(point.x + 1, point.y + orth_slope))
        p2 = Line.intersectionPoint(self, orth_line)
        return Point.distance(point, p2)

    def intersectsInfinite(self, other_line):
        """
        returns True if this line segment intersects the infinite line represented by the given line segment other_line,
        otherwise returns False.
        NOTE: unlike a lot of the other functions, this one is inclusive, meaning if this line 'pierces' the infinite line,
        it is considered to intersect it. However, colinearity is still not considered intersection
        """
        int_line = Line.intersectionPoint(self, other_line)
        xi, yi = int_line.x, int_line.y
        # print(self, xi, yi)

        if xi is None:  # parallel or colinear
            return False
        
        if self.slope is None:  # this line segment is vertical (other_line isn't - look at above return case)
            if min(self.p0.y, self.p1.y) <= yi <= max(self.p0.y, self.p1.y):
                return True
            else:
                return False
        else:  # this line
            if min(self.p0.x, self.p1.x) <= xi <= max(self.p0.x, self.p1.x):
                return True
            else:
                return False

    @staticmethod
    def intersects(l1, l2):
        """
        return True if the segments l1 and l2 intersect, else return False. Returns False in the case
        of colinearity
        """
        int_point = Line.intersectionPoint(l1, l2)
        ix, iy = int_point.x, int_point.y
        if ix is None:  # lines are parallel or colinear
            return False
        
        x_range = (min(l1.p0.x, l1.p1.x), max(l1.p0.x, l1.p1.x))
        if l1.slope is None:
            x_range = (min(l2.p0.x, l2.p1.x), max(l2.p0.x, l2.p1.x))  # l1 is vertical, so use x range from l2
        
        if x_range[0] < ix < x_range[1]:  # note: strict equality means the intersection can't occur at an endpoint
            return True
        else:
            return False
        
    @staticmethod
    def intersectionPoint(l1, l2):
        """
        get the intersection of the infinite lines corresponding to line segments l1 and l2.
        NOTE: does not check if the line _segments_ actually intersect. For that, use the Line.intersects function.

        in the case that l1 and l2 are colinear or parallel, returns (None, None)
        """
        if l1.slope == l2.slope:  # parallel check
            return None, None
        elif l1.slope is None:  # l1 is vertical
            return Point(l1.p0.x, l2.f(l1.p0.x))
        elif l2.slope is None:  # l2 is vertical
            return Point(l2.p0.x, l1.f(l2.p0.x))
        else:
            x = (l2.p0.y - l1.p0.y + (l1.slope*l1.p0.x) - (l2.slope*l2.p0.x)) / (l1.slope - l2.slope)
            y = l2.f(x)
            return Point(x, y)

    def __repr__(self):
        return f"({self.p0.x}, {self.p0.y})  -  ({self.p1.x}, {self.p1.y})"
    
    def __gt__(self, other):
        """
        NOTE: should only be used for parallel lines (ie, lines within the same tile)
        """
        if self.slope is None or other.slope is None:  # arbitrary decision
            return False
        return self.f(0) > other.f(0)  # test as function of x
    
    def __eq__(self, other):
        return self.p0 == other.p0 and self.p1 == other.p1


if __name__ == "__main__":
    l = Line(Point(0, 0), Point(1, 1))
    a = l
    print(a is l)