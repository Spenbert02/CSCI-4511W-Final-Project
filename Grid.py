"""
general info about the setup.

+y
^
|
|
|------> +x


The above coord system is used. bottom left tile is (0, 0).

Tile matrix indexing is flipped from usual. as shown below, row 0 is on the bottom, with successive rows stacked up.

  [...] ] 
  [...]
[ [...]
"""


import matplotlib.pyplot as plt
import numpy as np
from random import random
from Tile import Tile
from Line import Line
from Point import Point


class Grid:
    def __init__(self, num_rows, num_columns, min_angle, max_angle, tile_side_length, seed_tile_offset):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.w = tile_side_length
        self.offset = seed_tile_offset  # temporary, eventually this should be an allowable range of offsets?
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.tiles = []  # a 2D list of tiles, w/ [0][0] at bottom left (vertically flipped from standard 2d matrix representation)
        for i in range(self.num_rows):
            curr_row = []
            for j in range(self.num_columns):
                curr_row.append(Tile(self.w, None, Point(j*self.w, i*self.w), self.offset))  # note: giving angle as None. must be set before calling Tile methods
            self.tiles.append(curr_row)            

    def __repr__(self):
        return str(self.num_rows) + "x" + str(self.num_columns) + " grid - " + str(self.numLinesTraversed()) + " traversed"

    def getLines(self):
        ret_lines = []
        for row in self.tiles:
            for tile in row:
                ret_lines += tile.lines
        return ret_lines

    def numLinesTraversed(self):
        ret_val = 0
        for line in self.getLines():
            if line.traversed:
                ret_val += 1
        return ret_val
    
    def isFullyTraversed(self):
        return self.numLinesTraversed() == len(self.getLines())

    def getBorder(self):
        x = [0, 0, self.w * self.num_columns, self.w * self.num_columns, 0]
        y = [0, self.w * self.num_rows, self.w * self.num_rows, 0, 0]
        return [x, y]

    def printGrid(self):
        for i in range(self.num_rows - 1, -1, -1):
            for j in range(self.num_columns):
                print(str(round(self.tiles[i][j].angle, 3)).center(10) if self.tiles[i][j].angle is not None else "None".center(10), end="")
            print()
    
    def seedAngles(self, angle_array):
        """
        angle_array must have same shape as grid.
        """
        for i in range(len(angle_array)):  # rows
            for j in range(len(angle_array[i])):  # columns
                self.tiles[i][j].angle = angle_array[i][j]

    def randomGenAngles(self, start_angle, deviation_range):
        """
        start_angle: seed angle for bottom left tile
        deviation_range: deviation range for each random walk step
            angle can go +/- .5*deviation range
        """
        self.tiles[0][0].setAngle(start_angle)
        for i in range(self.num_rows):
            for j in range(self.num_columns):
                if (i, j) != (0, 0):  # skip bottom left (seed value)
                    i_par_val = None
                    j_par_val = None
                    if i >= 1:
                        i_par_val = self.tiles[i - 1][j].angle
                    if j >= 1:
                        j_par_val = self.tiles[i][j - 1].angle

                    new_angle_base = 0
                    if i_par_val is not None:
                        if j_par_val is not None:
                            new_angle_base = (i_par_val + j_par_val) / 2
                        else:
                            new_angle_base = i_par_val
                    else:
                        if j_par_val is not None:
                            new_angle_base = j_par_val
                        else:
                            new_angle_base = -999  # should never happen - bottom left corner is seeded.

                    rand_adjustment = (random() - .5)*deviation_range
                    new_angle = new_angle_base + rand_adjustment
                    if not (self.min_angle < new_angle < self.max_angle):
                        new_angle -= rand_adjustment
                        if rand_adjustment > self.max_angle:
                            # assumes rand_adjustment is greater than 0, which it will be because it went over the max
                            new_angle = self.max_angle - (rand_adjustment - (self.max_angle - new_angle_base))
                        else:  # went below min
                            # assumes rand_adjustment is less than 0, which it will be because it went below the min
                            new_angle = self.min_angle + (-rand_adjustment - (new_angle_base - self.min_angle))

                    self.tiles[i][j].setAngle(new_angle)
    
    def genTileLines(self):
        """
        generate the lines in each tile. currently generates line series with appropriate spacing and angle. seed line goes through tile center.
        
        old algo (not in use):
            1- generate seed tile lines.
            2- generate borders along bottom and left of grid that are continuous
            3- fill in internal tiles such that each line is continuous and the angles are as
               close as possible to the intended angle
        """

        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[0])):
                self.tiles[i][j].genLinesFromPoint(self.tiles[i][j].center)

        # # this code generates continuous lines, which was the original aim of the project. not enough time, so doing non-continuous lines.
        # # ------------------------
        # # generating seed tile lines
        # self.tiles[0][0].genLinesFromPoint((self.tiles[0][0].s_max/np.sin(self.tiles[0][0].angle), self.tiles[0][0].s_max/np.cos(self.tiles[0][0].angle)))
        
        # # filling out rest of tiles
        # for i in range(self.num_rows):
        #     for j in range(self.num_columns):
        #         tile = self.tiles[i][j]
        #         if (i, j) == (0, 0):  # skip this, seed tile already handled
        #             pass
        #         elif i >= 1 and j == 0:  # along left edge of tiles (excluding seed tile)
        #             ref_tile_points = self.tiles[i-1][0].getBorderPoints("T")
        #             x_offset = np.abs(ref_tile_points[1][0] - ref_tile_points[0][0])
        #             new_offset = x_offset * np.abs(np.sin(tile.angle * (np.pi / 180)))
        #             tile.genLinesFromPoint(ref_tile_points[0], offset=new_offset)
        #         elif i == 0 and j >= 1:  # along bottom edge of tiles (excluding seed tile)
        #             ref_tile_points = self.tiles[0][j - 1].getBorderPoints("R")
        #             y_offset = np.abs(ref_tile_points[1][1] - ref_tile_points[0][1])
        #             new_offset = y_offset * np.abs(np.cos(tile.angle * (np.pi / 180)))
        #             tile.genLinesFromPoint(ref_tile_points[0], offset=new_offset)
        #         else:  # has a tile both to the left and below it
        #             pass

    def getPrintableLines(self):
        """
        return a list of line objects that are printable given the current grid state
        NOTE: assumes that the angle range for lines is (0, -45)
        """
        ret_lines = []
        for i in range(len(self.tiles[0])):  # column by column
            printable_tiles_searched = 0
            for j in range(len(self.tiles)):  # row by row
                lines = self.tiles[j][i].lines

                k = 0
                while k < len(lines) and lines[k].traversed:
                    k += 1
                if k == len(lines):
                    continue

                if printable_tiles_searched == 0:
                    ret_lines.append(lines[k])
                    printable_tiles_searched += 1
                elif printable_tiles_searched == 1:
                    prev_line = ret_lines[-1]  # this will be the printable line in the tile below
                    if lines[k].p0.y < prev_line.f(lines[k].p0.x) and lines[k].p1.y < prev_line.f(lines[k].p1.x):
                        ret_lines.append(lines[k])
                    break
                
        return ret_lines

                
def showGridLines(grid, point_sequence=None, line_sequence=None):
    fig = plt.figure("Tile Lines")
    ax = fig.add_subplot()
    ax.set_ylim(-grid.w/2, grid.w*(grid.num_rows + .5))
    ax.set_xlim(-grid.w/2, grid.w*(grid.num_columns + .5))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect(1)
    ax.axis("on")
    
    # tile border lines
    for i in range(grid.num_rows):
        for j in range(grid.num_columns):
            borders = grid.tiles[i][j].getBorder()
            ax.plot(borders[0], borders[1], "#000000", lw=.5)  

    # grid border (thicker so looks decent)
    border = grid.getBorder()
    ax.plot(border[0], border[1], color="#000000", lw=.5)

    # tile lines.
    if line_sequence is None:
        for i in range(grid.num_rows):
            for j in range(grid.num_columns):
                lines = grid.tiles[i][j].lines
                for line in lines:
                    ax.plot((line.p0.x, line.p1.x), (line.p0.y, line.p1.y), color='r', lw=2)
                    # if line.test:  # FOR TESTING PURPOSES
                    #     ax.plot((line.p0.x, line.p1.x), (line.p0.y, line.p1.y), color='g', lw=2)
                    # elif line.traversed:
                    #     ax.plot((line.p0.x, line.p1.x), (line.p0.y, line.p1.y), color='b', lw=2)
                    # else:
                    #     ax.plot((line.p0.x, line.p1.x), (line.p0.y, line.p1.y), color='r', lw=2)
    else:
        for i in range(len(line_sequence)):
            if i > 0:
                last_line = Line(point_sequence[2*i - 1], point_sequence[2*i])
                ax.plot((last_line.p0.x, last_line.p1.x), (last_line.p0.y, last_line.p1.y), color='b', lw=2)
            line = line_sequence[i]
            ax.plot((line.p0.x, line.p1.x), (line.p0.y, line.p1.y), color='r', lw=2)

    # # data labels (ordering)
    # if point_sequence is not None:
    #     for i in range(len(point_sequence)):
    #         ax.text(point_sequence[i].x, point_sequence[i].y, str(i+1), fontsize=10, va='top', ha="left", color="grey")

    plt.show()

def showGridAngles(grid):
    fig = plt.figure("Tile Orientations")
    ax = fig.add_subplot()
    ax.set_ylim(-grid.w/2, grid.w*(grid.num_rows + .5))
    ax.set_xlim(-grid.w/2, grid.w*(grid.num_columns + .5))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect(1)
    ax.axis("on")

    # tile lines
    for i in range(grid.num_rows):
        for j in range(grid.num_columns):
            borders = grid.tiles[i][j].getBorder()
            ax.plot(borders[0], borders[1], "#000000", lw=2)
    
    # # center dots
    # dots = [[], []]
    # for i in range(grid.num_rows):
    #     for j in range(grid.num_columns):
    #         dots[0].append(grid.w * (j + .5))
    #         dots[1].append(grid.w * (i + .5))
    # ax.plot(dots[0], dots[1], 'ro')

    # lines
    for i in range(grid.num_rows):
        for j in range(grid.num_columns):
            if grid.tiles[i][j].angle is not None:
                center_coords = [grid.w*(j + .5), grid.w*(i + .5)]
                angle = grid.tiles[i][j].angle
                l = grid.w / 3
                p1 = [center_coords[0] + (l/2)*np.cos(angle*(np.pi/180)), center_coords[1] + (l/2)*np.sin(angle*(np.pi/180))]
                p2 = [center_coords[0] - (l/2)*np.cos(angle*(np.pi/180)), center_coords[1] - (l/2)*np.sin(angle*(np.pi/180))]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='b', lw=2)

    plt.show()


def lineTest():
    """
    paper continuous example:
    -30.346 -44.004
    -45.000 -39.422
    """
    test = Grid(2, 2, -45, 0, 1, .1)
    # test.randomGenAngles(-45, 45)
    test.tiles[0][0].angle = -45.000
    test.tiles[0][1].angle = -39.422
    test.tiles[1][0].angle = -30.346
    test.tiles[1][1].angle = -44.004
    test.genTileLines()
    print(test.tiles[0][0].lines[0])

    # for i in range(10):
    #     test.tiles[0][0].lines[i].traversed = True
    # for i in range(3):
    #     test.tiles[0][1].lines[i].traversed = True
    # for i in range(2):
    #     test.tiles[1][0].lines[i].traversed = True
    # pls = test.getPrintableLines()
    # for line in pls:
    #     line.traversed = True
    #     line.test = True

    showGridLines(test)

def paperFig3():
    fig = plt.figure("Tile Orientations")
    ax = fig.add_subplot()
    ax.set_ylim(-.1, 2.1)
    ax.set_xlim(-.1, 1.1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect(1)
    ax.axis("off")

    # angle stuff
    ax.plot((0, .6), (1.2, 1.2), color="grey", linestyle="dashed", lw=1)
    ax.text(.15, 1.07, r'$-45^\circ$', fontsize=10, va='bottom', color="grey")    
    r = .15
    theta = np.linspace(0, -np.pi/4, 20)
    ax.plot(r*np.cos(theta), 1.2 + r*np.sin(theta), color="grey", lw=1)

    # red lines
    ax.plot((0, .2), (1.2, 1), color='r', lw=2)
    ax.plot((.4, 1), (1, .4), color='r', lw=2)

    # borders
    ax.plot((0, 1, 1, 0, 0), (0, 0, 2, 2, 0), "#000000", lw=2)
    ax.plot((0, 1), (1, 1), "#000000", lw=2)

    plt.show()

if __name__ == "__main__":
    lineTest()
    # paperFig3()
