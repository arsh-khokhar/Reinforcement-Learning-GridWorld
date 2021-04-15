from enum import Enum
import random


class Action(Enum):
    north = [1, 0]
    east = [0, 1]
    west = [0, -1]
    south = [-1, 0]
    exit_game = [0, 0]


ACTION_NEIGHBOURS = {Action.north: [Action.west, Action.east],
                     Action.east: [Action.north, Action.south],
                     Action.west: [Action.north, Action.south],
                     Action.south: [Action.west, Action.east],
                     Action.exit_game: [Action.exit_game]}


class State:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.q_values = {Action.north: 0.0, Action.east: 0.0,
                         Action.west: 0.0, Action.south: 0.0}
        self.value = 0.0
        self.is_terminal = False
        self.is_boulder = False
        self.reward = 0.0
        self.best_action = None
        self.terminal_reward = 0.0

    def get_actions(self):
        return self.q_values.keys()

    def print_state(self, print_qvals=False):
        print("State {},{} \tValue: {:.2f} \tBest action: {}".format(
            self.row, self.col, self.value, self.best_action))
        if print_qvals:
            for q in self.q_values:
                print("\taction: {} q_value: {}".format(q, self.q_values[q]))


class Grid:

    def load_from_file(self, filename):
        self.action_neighbours = {Action.north: [Action.west, Action.east],
                                  Action.east: [Action.north, Action.south],
                                  Action.west: [Action.north, Action.south],
                                  Action.south: [Action.west, Action.east],
                                  Action.exit_game: [Action.exit_game]}
        self.num_rows = 0
        self.num_cols = 0
        self.terminals = []
        self.boulders = []
        self.robot_start_location = [None, None]
        self.robot_curr_location = [None, None]
        self.k = None
        self.episodes = None
        self.discount = None
        self.transition_cost = None
        self.alpha = None
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
                value = value.strip()[1:-1]
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
                value = value.strip()[1:-1]
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
                self.k = int(value.strip())

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

        self.states = []

        for i in range(self.num_rows):
            new_row = []
            for j in range(self.num_cols):
                new_state = State(i, j)
                new_state.reward = self.transition_cost
                new_row.append(new_state)
            self.states.append(new_row)

        self.max_terminal_val = abs(self.transition_cost)+1e-10
        for terminal in self.terminals:
            self.states[terminal[0]][terminal[1]].q_values = {
                Action.exit_game: 0.0}
            self.states[terminal[0]][terminal[1]].terminal_reward = terminal[2]
            self.states[terminal[0]][terminal[1]].is_terminal = True
            if self.max_terminal_val < abs(terminal[2]):
                self.max_terminal_val = abs(terminal[2])

        for boulder in self.boulders:
            self.states[boulder[0]][boulder[1]].is_boulder = True

    def print_states(self):
        for row in self.states:
            for state in row:
                state.print_state()

    def find_possible_states(self, row, col):
        state = self.states[row][col]
        possible_states = {}
        for action in state.get_actions():
            dest_row = row + action.value[0]
            dest_col = col + action.value[1]
            if dest_row >= 0 and dest_row < self.num_rows and \
                    dest_col >= 0 and dest_col < self.num_cols and not \
                    self.states[dest_row][dest_col].is_boulder:
                possible_states[action] = self.states[dest_row][dest_col]
            else:
                possible_states[action] = state
        return possible_states

    def load_results(self, filename):
        self.mdp_results = []
        self.rl_results = []

        with open(filename, 'r') as fp:
            lines = fp.readlines()

        for line in lines:
            row, col, number, learning_type, query = line.split(',')
