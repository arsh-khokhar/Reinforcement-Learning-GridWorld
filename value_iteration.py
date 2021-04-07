from enum import Enum
import random


class Action(Enum):
    north = [-1, 0]
    east = [0, 1]
    west = [0, -1]
    south = [1, 0]
    exit_game = [0, 0]


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
        self.grid_size = {}
        self.terminals = []
        self.boulders = []
        self.robot_location = [None, None]
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

            if attr.lower() == "horizontal" or attr.lower() == "vertical":
                self.grid_size[attr.lower()] = int(value.strip())

            elif attr.lower() == "terminal":
                value = value.strip()[1:-1]
                while len(value) > 0:
                    start_index = value.find('{', 1)
                    end_index = value.find('}') + 1
                    terminal_values = value[start_index:end_index][1:-1]
                    unpacked = terminal_values.split(',')
                    hor, vert, cost = int(
                        unpacked[0]) - 1, int(unpacked[1]) - 1, float(unpacked[2])
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
                    self.boulders.append([hor - 1, vert - 1])
                    value = value[end_index + 1:]

            elif attr.lower() == "robotstartstate":
                value = value.strip()[1:-1]
                unpacked = value.split(',')
                self.robot_location = [
                    int(unpacked[0]) - 1, int(unpacked[1]) - 1]

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

        for i in range(self.grid_size["vertical"]):
            new_row = []
            for j in range(self.grid_size["horizontal"]):
                new_state = State(i, j)
                new_state.reward = self.transition_cost
                new_row.append(new_state)
            self.states.append(new_row)

        self.max_terminal_val = abs(self.transition_cost)
        for terminal in self.terminals:
            self.states[terminal[0]][terminal[1]].q_values = {
                Action.exit_game: 0.0}  # terminal[2]}
            self.states[terminal[0]][terminal[1]].reward = terminal[2]
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
            if dest_row >= 0 and dest_row < self.grid_size["vertical"] and \
                    dest_col >= 0 and dest_col < self.grid_size["horizontal"] and not \
                    self.states[dest_row][dest_col].is_boulder:
                possible_states[action] = self.states[dest_row][dest_col]
            else:
                possible_states[action] = state
        return possible_states

    def get_action_neighbours(self, action):
        action_neighbours = {Action.north: [Action.west, Action.east],
                             Action.east: [Action.north, Action.south],
                             Action.west: [Action.north, Action.south],
                             Action.south: [Action.west, Action.east],
                             Action.exit_game: [Action.exit_game]}
        return action_neighbours[action]

    def iterate_value(self, row, col):
        state = self.states[row][col]
        possible_states = self.find_possible_states(row, col)

        for action in state.get_actions():
            summation = 0.0
            summation += (1.0 - self.noise) * \
                (possible_states[action].reward +
                 self.discount*possible_states[action].value)

            for neighbour in self.get_action_neighbours(action):
                summation += (self.noise / 2.0) * (
                    possible_states[neighbour].reward + self.discount*possible_states[neighbour].value)

            state.q_values[action] = summation

    def find_max_q_value(self, row, col):
        state = self.states[row][col]
        if not state.is_boulder:
            best_action = None
            max_q_value = float('-inf')
            for key in state.q_values:
                if state.q_values[key] > max_q_value:
                    max_q_value = state.q_values[key]
                    best_action = key
                if self.max_terminal_val < abs(state.q_values[key]):
                    self.max_terminal_val = abs(state.q_values[key])
        return max_q_value, best_action

    def update(self, row, col, action, dest_row, dest_col):
        if row == 0 and col == 2:
            x = "do nothing" 
        state = self.states[row][col]
        dest_state = self.states[dest_row][dest_col]

        sample = dest_state.reward + self.discount * \
            self.find_max_q_value(dest_row, dest_col)[0]

        state.q_values[action] = (1-self.alpha) * \
            state.q_values[action] + self.alpha*sample

    def get_policy(self, row, col):
        possible_states = self.find_possible_states(row, col)

        max_q_value = float('-inf')
        best_action_state_pairs = []
        for action, possible_state in possible_states.items():
            curr_max_q = self.find_max_q_value(
                possible_state.row, possible_state.col)[0]
            if curr_max_q > max_q_value:
                best_action_state_pairs = [(action, possible_state)]
                max_q_value = curr_max_q
            elif curr_max_q == max_q_value:
                best_action_state_pairs.append((action, possible_state))

            best_random = random.choice(best_action_state_pairs)
            some_rand = random.uniform(0.0, 1.0)
            if some_rand < self.noise:
                action_neighbours = self.get_action_neighbours(best_random[0])
                best_random = (best_random[0], possible_states[random.choice(
                    action_neighbours)])
        return best_random

    def q_learn(self):
        # for i in range(self.episodes):
        robot_curr_row = self.robot_location[0]
        robot_curr_col = self.robot_location[1]
        # curr_state = self.states[robot_curr_row][robot_curr_col]
        while True:
            best_action, next_state = self.get_policy(
                robot_curr_row, robot_curr_col)
            self.update(robot_curr_row, robot_curr_col,
                        best_action, next_state.row, next_state.col)
            robot_curr_row = next_state.row
            robot_curr_col = next_state.col
            if best_action == Action.exit_game:
                break

    def update_values(self):
        # updating the values
        for row in self.states:
            for state in row:
                if not state.is_boulder:
                    best_action = None
                    max_q_value = float('-inf')
                    for key in state.q_values:
                        if state.q_values[key] > max_q_value:
                            max_q_value = state.q_values[key]
                            best_action = key
                        if self.max_terminal_val < abs(state.q_values[key]):
                            self.max_terminal_val = abs(state.q_values[key])
                    state.value = max_q_value
                    state.best_action = best_action

    def iterate_values(self, k):
        for i, row in enumerate(self.states):
            for j, state in enumerate(row):
                if not state.is_terminal and not state.is_boulder:
                    self.iterate_value(i, j)
        self.update_values()
