"""
    File name: grid.py
    Author: Arsh Khokhar, Kiernan Wiese
    Date last modified: 15 April, 2021
    Python Version: 3.8
    This script contains the grid and state classes used to keep track of
    values for both q learning and value iteration as those algorithms run.
"""
from enum import Enum


class Action(Enum):
    """
    Enum class used to represent what indexes change when a given move is chosen
    """
    north = [1, 0]
    east = [0, 1]
    west = [0, -1]
    south = [-1, 0]
    exit_game = [0, 0]


# used in cases where there is uncertainty to see where else the robot can end up
ACTION_NEIGHBOURS = {Action.north: [Action.west, Action.east],
                     Action.east: [Action.north, Action.south],
                     Action.west: [Action.north, Action.south],
                     Action.south: [Action.west, Action.east],
                     Action.exit_game: [Action.exit_game]}


class State:
    """
    Representation of a state
    Attributes
        row                 The row the state is located at
        col                 The column the state is located at
        q_values            The q_values for each action at a state
        max_q_value         The max q value from q_values
        is_terminal         True if the state is terminal, false otherwise
        is_boulder          True if the state is a boulder, false otherwise
        reward              The reward for visiting this state
        best_action         The action that has max_q_value
        terminal_reward     The reward for exiting the game from this state
                            (non-zero only if is_terminal is true)
    """

    def __init__(self, row, col):
        """
        Constructor of a state
        :param row: The row the state is located at
        :param col: The column the state is located at
        """
        self.row = row
        self.col = col
        self.q_values = {Action.north: 0.0, Action.east: 0.0,
                         Action.west: 0.0, Action.south: 0.0}
        self.max_q_value = 0.0
        self.is_terminal = False
        self.is_boulder = False
        self.reward = 0.0
        self.best_action = None
        self.terminal_reward = 0.0

    def get_actions(self):
        """
        :return: The actions that a state can take
        """
        return self.q_values.keys()

    def print_state(self, print_qvals=False):
        """
        :param print_qvals: True to print q values, false to not
        """
        print("State {},{} \tValue: {:.2f} \tBest action: {}".format(
            self.row, self.col, self.max_q_value, self.best_action))
        if print_qvals:
            for q in self.q_values:
                print("\taction: {} q_value: {}".format(q, self.q_values[q]))


class Grid:
    """
    Representation of a grid
    Attributes
        num_rows                Number of rows in the grid
        num_cols                Number of columns in the grid
        terminals               Locations of all terminal states
        boulders                Locations of all boulder states
        robot_start_location    Start location of the robot
        robot_curr_location     Current location of the robot
        iterations              Number of times to do value iteration
        episodes                Number of episodes to do q learning on
        discount                Discount value for learning
        transition_cost         Cost for trasitioning between states
        alpha                   Value of alpha
        states                  Multidimensional array of state objects, that
                                represent the grid.
        max_terminal_val        keeps track of the maximum terminal value for 
                                darker/lighter GUI colors
    """

    def __init__(self, filename):
        """
        Init the grid class from a file
        :param filename: The name of the file to load the grid from (gridConf.txt)
        """
        self.num_rows = 0
        self.num_cols = 0
        self.terminals = []
        self.boulders = []
        self.robot_start_location = [None, None]
        self.robot_curr_location = [None, None]
        self.iterations = None
        self.episodes = None
        self.discount = None
        self.transition_cost = None
        self.alpha = None
        self.states = []
        self.max_terminal_val = 0

        with open(filename, 'r') as fp:
            lines = fp.readlines()

        for line in lines:
            line_contents = line.split('=', 1)

            attr, value = line_contents[0], line_contents[1]

            if attr.lower() == "horizontal":
                self.num_rows = int(value.strip())

            elif attr.lower() == "vertical":
                self.num_cols = int(value.strip())

            elif attr.lower() == "terminal":
                value = value.strip()
                if not value.endswith('}}\n'):
                    value = value + '}'
                value = value[1:-1]
                while len(value) > 0:
                    start_index = value.find('{', 1)
                    end_index = value.find('}') + 1
                    terminal_values = value[start_index:end_index][1:-1]
                    unpacked = terminal_values.split(',')
                    hor, vert, cost = int(
                        unpacked[0]), int(unpacked[1]), float(unpacked[2])
                    self.terminals.append([hor, vert, cost])
                    value = value[end_index + 1:]

            elif attr.lower() == "boulder":
                value = value.strip()
                if not value.endswith('}}\n'):
                    value = value + '}'
                value = value[1:-1]
                while len(value) > 0:
                    start_index = value.find('{', 1)
                    end_index = value.find('}') + 1
                    terminal_values = value[start_index:end_index][1:-1]
                    unpacked = terminal_values.split(',')
                    hor, vert = int(unpacked[0]), int(unpacked[1])
                    self.boulders.append([hor, vert])
                    value = value[end_index + 1:]

            elif attr.lower() == "robotstartstate":
                value = value.strip()[1:-1]
                unpacked = value.split(',')
                self.robot_start_location = [
                    int(unpacked[0]), int(unpacked[1])]
                self.robot_curr_location = [
                    int(unpacked[0]), int(unpacked[1])]

            elif attr.lower() == "k":
                self.iterations = int(value.strip())

            elif attr.lower() == "episodes":
                self.episodes = int(value.strip())

            elif attr.lower() == "alpha":
                self.alpha = float(value.strip())

            elif attr.lower() == "discount":
                self.discount = float(value.strip())

            elif attr.lower() == "noise":
                self.noise = float(value.strip())

            elif attr.lower() == "transitioncost":
                self.transition_cost = float(value.strip())

        for i in range(self.num_rows):
            new_row = []
            for j in range(self.num_cols):
                new_state = State(i, j)
                new_state.reward = self.transition_cost
                new_row.append(new_state)
            self.states.append(new_row)

        for terminal in self.terminals:
            self.states[terminal[0]][terminal[1]].q_values = {
                Action.exit_game: 0.0}
            self.states[terminal[0]][terminal[1]].terminal_reward = terminal[2]
            self.states[terminal[0]][terminal[1]].is_terminal = True
            # updating the max_termial for GUI colors
            if self.max_terminal_val < abs(terminal[2]):
                self.max_terminal_val = abs(terminal[2])

        for boulder in self.boulders:
            self.states[boulder[0]][boulder[1]].is_boulder = True

    def print_states(self):
        """
        Print all states
        """
        for row in self.states:
            for state in row:
                state.print_state()

    def find_possible_states(self, row, col):
        """
        Find the states the robot can move to from another state

        :param row: The row of the state to check
        :param col: The column of the state to check
        :return: A dictionary containing which actions lead to which states
        """
        state = self.states[row][col]
        possible_states = {}
        for action in state.get_actions():
            # getting the destination cell corresponding to an action
            dest_row = row + action.value[0]
            dest_col = col + action.value[1]
            if 0 <= dest_row < self.num_rows and \
                    0 <= dest_col < self.num_cols and not \
                    self.states[dest_row][dest_col].is_boulder:
                possible_states[action] = self.states[dest_row][dest_col]
            else:
                possible_states[action] = state
        return possible_states
