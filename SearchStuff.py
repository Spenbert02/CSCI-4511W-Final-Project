import copy
import numpy as np
import sys
sys.path.append("aima-python")

from Grid import Grid, showGridLines
from Line import Line
from Point import Point
from search import *


class ToolpathProblem(Problem):
    """
    state representation:
    [grid: Grid, current_line: Line, current_point: Point, traversal_distance: distance of total non-extrude movements, needed for local searches]
    """

    def actions(self, state):
        """
        return a list of possible points to traverse to
        each action is [Line, Point]. this might need to be an iterator instead
        """
        grid = state[0]
        printable_lines = grid.getPrintableLines()
        actions = []
        for line in printable_lines:
            actions.append([line, line.p0])
            actions.append([line, line.p1])

        return actions
    
    def result(self, state, action):
        """
        returns state in form [grid, current line, current point, distance]
        """

        ret_state = [copy.deepcopy(state[0])]
        # print("************* ", ret_state[0].numLinesTraversed())
        # change action line to be traversed and change current point
        action_line = action[0]
        for line in ret_state[0].getLines():
            # print(line, " | ", action_line, end="")
            if line == action_line:
                # print(" *", end="")
                line.traversed = True
                ret_state.append(line)
                if action[1] == line.p0:  # point moving to is line.p0
                    ret_state.append(line.p1)  # p1 is end point of travel, so new current position
                else:
                    ret_state.append(line.p0)
            # print()
        ret_state.append(Point.distance(state[2], action[1]))  # distance of travel

        return ret_state
    
    def goal_test(self, state):
        """
        return true if all lines are traversed, otherwise return false
        """
        grid = state[0]
        for line in grid.getLines():
            if not line.traversed:
                return False
        return True
    
    def path_cost(self, c, state1, action, state2):
        """
        return distance between the current point in state1 to the point traveled to by action
        """
        old_point = state1[2]
        new_point = action[1]
        return c + Point.distance(old_point, new_point)
    
    def value(self, state):
        """
        value is the maximum possible travel distance (diagonal of grid) minus the distance of the last non-extrude movement.
        Basically, local searches will attempt to maximize this, which will minimize the distance travelled to get to this state.
        """
        # print(state)
        return (state[0].numLinesTraversed() * state[0].num_columns * state[0].w * np.sqrt(2)) - state[3]
    
    def totalCost(self, action_sequence, add_cost=None):
        """
        given action sequence, return cost of non-extruding movements
        """
        ret_cost = 0 if add_cost is None else add_cost
        for i in range(len(action_sequence) - 1):
            line_end_point = action_sequence[i][0].p0 if action_sequence[i][1] == action_sequence[i][0].p1 else action_sequence[i][0].p1  # ending point of old line
            line_start_point = action_sequence[i + 1][1]  # starting point of new line
            ret_cost += Point.distance(line_end_point, line_start_point)
        return ret_cost
    
    # def h(self, node):
    #     grid = node.state[0]
    #     last_distance = 


def main():
    """
    results:
    2x2:
        - su: 52, G0: 0, St: 224
        - total J(C): 8.3400
    4x4:
        - su: 200, G0: 0, St: 1206
        - total J(C): 33.644
    """

    # grid 1: a 2 by 2 grid, used in the paper
    grid1 = Grid(2, 2, -45, 0, 1, .1)
    grid1.randomGenAngles(-45, 45)
    # grid1.tiles[0][0].angle = -45.000
    # grid1.tiles[0][1].angle = -39.422
    # grid1.tiles[1][0].angle = -30.346
    # grid1.tiles[1][1].angle = -44.004
    grid1.genTileLines()

    # initialize grid for problem: first toolpath is bottom left, ending point of movement is the higher one.
    init_line = grid1.tiles[0][0].lines[0]
    init_line.traversed = True
    init_endpoint = None
    starting_point = None
    if init_line.p0.y > init_line.p1.y:
        init_endpoint = init_line.p0
        starting_point = init_line.p1
    else:
        init_endpoint = init_line.p1
        starting_point = init_line.p0
    init_state = [grid1, init_line, init_endpoint, init_line.length()]

    # solving with hill climbing
    grid_prob_1 = InstrumentedProblem(ToolpathProblem(init_state))
    result = hill_climbing(grid_prob_1)
    print("Su: Successor States created")
    print("Go: Number of Goal State checks")
    print("St: States created")
    print("   Su   Go   St")
    print(grid_prob_1)

    # putting actions into point travel sequence
    point_sequence = [starting_point, init_endpoint]
    for action in result.solution():
        # print(action)
        line = action[0]
        line_start_point = action[1]
        point_sequence.append(line_start_point)
        point_sequence.append(line.p0 if line.p1 == line_start_point else line.p1)

    # putting lines into line sequence
    line_sequence = [init_line]
    for action in result.solution(): line_sequence.append(action[0])

    # getting total solution cost (sum of non-extruded travels)
    total_cost = grid_prob_1.totalCost(result.solution(), Point.distance(init_endpoint, result.solution()[0][1]))
    print(total_cost)

    showGridLines(grid1, point_sequence, line_sequence)


if __name__ == "__main__":
    main()
