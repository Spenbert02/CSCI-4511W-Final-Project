import copy
import matplotlib.pyplot as plt
import numpy as np
from Line import Line
from Point import Point


class Tile:
    def __init__(self, w, angle, p0, s_max):
        """
        w: side length of tile
        angle: line offset angle (counter clockwise from +x axis)
            +y
            ^   /
            |  /
            | / angle
            |/________> +x
        p_0: location of bottom left point (where tile is in outside coord system)
        s_max: max orthogonal distance between lines in a tile
        """
        self.w = w
        self.angle = angle
        self.p0 = p0
        self.s_max = s_max
        self.lines = []  # list of lines, each in the form [[x0, y0], [x1, y1]]. Although no travel order should be determined from 0 or 1 subscript
        self.center = Point(self.p0.x + (w/2), self.p0.y + (w/2))  # useful to have
        self._initializeBorders()

        if self.angle is not None:  # angle can be initialized to zero. must be set before calling any Tile methods tho 
            self._normalizeAngle()  # bring angle to within (-90, 90)
    
    def setAngle(self, new_angle):
        self.angle = new_angle
        if self.angle is not None:
            self._normalizeAngle()

    def getBorderPoints(self, border_char):
        """
        border_char must be either "L", "T", "R", or "B".
        returns points in [[x1, y1], [x2, y2], ...] format
        """
        border_dict = {"L":0, "T":1, "R":2, "B":3}
        border_line = self.border_lines[border_dict[border_char]]
        ret_points = []
        for line in self.lines:
            if border_line.intersectsInfinite(line):
                ret_points.append(Line.intersectionPoint(border_line, line))
        return ret_points

    def _normalizeAngle(self):
        self.angle = (np.abs(self.angle) % 180) * (np.abs(self.angle) / self.angle)
        if self.angle > 90:  # quad II
            self.angle -= 180
        elif self.angle > 0:  # quad I, okay
            pass
        elif self.angle > -90:  # quad IV, okay
            pass
        else:  # quad III
            self.angle = 180 - np.abs(self.angle)

    def _initializeBorders(self):
        """
        initialize the borders of this tile, should be called upon when this object is constructed
        """
        c0 = self.p0  # bottom left
        c1 = Point(self.p0.x, self.p0.y + self.w)  # top left
        c2 = Point(self.p0.x + self.w, self.p0.y + self.w)  # top right
        c3 = Point(self.p0.x + self.w, self.p0.y)  # bottom right
        self.border_lines = (
            Line(c0, c1),  # left border
            Line(c1, c2),  # top border
            Line(c2, c3),  # right border
            Line(c3, c0)  # bottom border
        )

    # functions for generating lines
    def genLinesFromPoint(self, point, offset=None):
        """
        generate lines in a tile, given a seed point and the angle of the tile. If lines already exist, this will clear them first. If
        the line resulting from the tile and and seed point is not in the tile, also returns False
        """
        slope = np.tan(self.angle * (np.pi / 180))
        if np.abs(slope) > 10**5:  # vertical line
            slope = None
            seed_line = Line(point, Point(point.x, point.y + 1))
        else:  # defined slope
            if np.abs(slope) < 10**(-5):  # essentially zero slope
                slope = 0
            seed_line = Line(point, Point(point.x + 1, point.y + slope))
        
        if not self.inTile(seed_line):  # ensure seed line is in tile
            return False
        
        offset = self.s_max if offset is None else offset  # use default offset if none given
        self.lines.clear()
        initial_line = copy.deepcopy(seed_line)
        while self.addLine(copy.deepcopy(seed_line)):  # translate in positive orthogonal direction
            seed_line.translateOrthogonal(offset)

        seed_line = initial_line
        seed_line.translateOrthogonal(-offset)
        while self.addLine(copy.deepcopy(seed_line)):  # translate in negative orthogonal direction
            seed_line.translateOrthogonal(-offset)

    # helper functions for line stuff
    def inTile(self, line: Line):
        """
        given a line segment, determine if the infinite line it falls on intersects with the tile.
        NOTE: if the given line falls on one of the borders, it is considered to be in the tile. if it intersects a corner, it is not.
        """
        
        # determine how many corners are intersected.
        corners_intersected = 0
        for border in self.border_lines:
            if np.abs(line.orthogonalDistance(border.p0)) < 10**(-5):  # border.p0 will iterate over all four corner points
                corners_intersected += 1
        if corners_intersected == 1:  # only one corner intersected, so line is not considered to be in tile
            return False

        # logic synopsis here: if the infinite line represented by the line segment 'line' intersects any of the borders,
        # it must intersect two of the borders (we don't consider colinearity intersection). Therefore, check if 'line' intersects
        # any borders, and if it does return true.
        for border_line in self.border_lines:
            if border_line.intersectsInfinite(line):
                return True
        return False  # at this point, no intersections were found. line not in tile.
    
    def lineSegInTile(self, line):
        """
        given a line segment, return a new, colinear line segment that intersects the tile on its borders. assumes the given
        line segment intersects the tile border at two places - ie, not exactly on a corner.
        """
        intersections = [None, None, None, None]  # indicates intersection points of (L, T, R, B) border segments with given line
        for i in range(4):
            border = self.border_lines[i]
            if border.intersectsInfinite(line):
                intersections[i] = Line.intersectionPoint(border, line)
        
        while None in intersections:  # this function assumes the line will intersect this tile border set at two points, so remove the two None's to get the points
            intersections.remove(None)
        return Line(intersections[0], intersections[1])  # make line from two remaining points

    # functions for visualization:
    def getBorder(self):
        """
        get a 2D tuple representing the border of the tile in the format ((x1, ..., x5), (y1, ..., y5)). Takes 5
        points to define the outer border
        """
        x = [self.p0.x, self.p0.x, self.p0.x + self.w, self.p0.x + self.w, self.p0.x]
        y = [self.p0.y, self.p0.y + self.w, self.p0.y + self.w, self.p0.y, self.p0.y]
        return [x, y]
    
    def addLine(self, line):
        """
        add a segmented line to the tile. return True if successfully added, False if not (ie. line was not in tile).
        lines are added in order of bottom to top.
        """
        if self.inTile(line):  # line is
            seg_line = self.lineSegInTile(line)

            if seg_line.length() < self.w / 10:  # arbitrary, makes viewing easier
                return False

            if len(self.lines) == 0:  # no lines, just insert
                self.lines.append(seg_line)
                return True
            
            i = 0
            while i < len(self.lines) and seg_line > self.lines[i]:  # keep incrementing i such that i is the index that the new line needs to be inserted at
                i += 1
            
            self.lines.insert(i, seg_line)
            return True
        else:
            return False

    def getLines(self):
        """
        get the lines in a tile in a 3D tuple of the format:
        (
            ((l1_x0, l1_x1), (l1_y0, l1_y1)),
            ((l2_x0, l2_x1), (l2_y0, l2_y1)),
            ...
        )
        If the lines in a tile have not been generated, returns empty tuple.
        """
        ret_lines = []
        for line in self.lines:
            x = line.xList()
            y = line.yList()
            ret_lines.append((x, y))
        
        return tuple(ret_lines)


def test():
    val = -56
    print(val)
    val = (np.abs(val) % 180) * (np.abs(val) / val)
    if val > 90:  # quadrant II
        val = val - 180
    elif val > 0:  # quadrant I - okay
        pass
    elif val > -90:  # quadrant IV - okay
        pass
    else:  # quadrant III
        val = 180 - np.abs(val)
    print(val)

def main():
    tile = Tile(1, 820.819, Point(0, 0), .1)
    tile.genLinesFromPoint(Point(0, .1))
    for line in tile.lines:
        print(line)

    # tile = Tile(1, 0, (0, 0), .1)
    # tile.lines = [Line((0, .5), (1, .5))]

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlim(-.1, 1.1)
    ax.set_ylim(-.1, 1.1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect(1)
    ax.axis("off")

    # plotting lines
    for line in tile.getLines():
        ax.plot(line[0], line[1], color='r', lw=2)

    # plotting border
    border = tile.getBorder()
    ax.plot(border[0], border[1], color='0', lw=2)
    
    plt.show()


if __name__ == "__main__":
    # main()
    # test()
    a = [1, 3]
    a.insert(1, 2)
    print(a)