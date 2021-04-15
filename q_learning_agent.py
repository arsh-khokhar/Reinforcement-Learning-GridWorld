import random
from grid import Grid, Action, ACTION_NEIGHBOURS


class QLearningAgent:

    def __init__(self, input_grid: Grid):
        self.grid = input_grid
        self.discount = input_grid.discount
        self.noise = input_grid.noise
        self.alpha = input_grid.alpha
        self.max_display_val = input_grid.max_terminal_val
        self.episodes = 0

    def find_max_q_value(self, row, col):
        state = self.grid.states[row][col]
        if not state.is_boulder:
            best_action = None
            max_q_value = float('-inf')
            for key in state.q_values:
                if state.q_values[key] > max_q_value:
                    max_q_value = state.q_values[key]
                    best_action = key
                if self.max_display_val < abs(state.q_values[key]):
                    self.max_display_val = abs(state.q_values[key])
            return max_q_value, best_action
        return 0.0, None

    def update(self, row, col, action, dest_row, dest_col):
        move_success = True
        if dest_row >= self.grid.num_rows or dest_row < 0 \
                or dest_col >= self.grid.num_cols or dest_col < 0 \
                or self.grid.states[dest_row][dest_col].is_boulder:
            dest_row = row
            dest_col = col
            move_success = False
        state = self.grid.states[row][col]
        if action not in state.get_actions():
            print("{} is not a valid action for the cell ({},{})".format(
                action, row, col))
            return False

        if action == Action.exit_game:
            sample = state.terminal_reward
            self.grid.robot_curr_location = self.grid.robot_start_location[:]
        else:
            sample = state.reward + self.discount * \
                self.find_max_q_value(dest_row, dest_col)[0]
            self.grid.robot_curr_location = [dest_row, dest_col]

        state.q_values[action] = (1-self.alpha) * \
            state.q_values[action] + self.alpha*sample

        return move_success

    # def get_policy(self, row, col):
    #     state = self.grid.states[row][col]
    #     possible_states = self.grid.find_possible_states(row, col)

    #     max_q_value = float('-inf')
    #     best_actions = []
    #     for action, value in state.q_values.items():
    #         if value > max_q_value:
    #             best_actions = [action]
    #             max_q_value = value
    #         elif value == max_q_value:
    #             best_actions.append(action)

    #     best_random = random.choice(best_actions)
    #     state = possible_states[best_random]
    #     some_rand = random.uniform(0.0, 1.0)
    #     if some_rand < self.noise:
    #         action_neighbours = ACTION_NEIGHBOURS[best_random]
    #         state = possible_states[random.choice(action_neighbours)]

    #     return best_random, state

    # def q_learn(self):
    #     robot_curr_row = self.grid.robot_location[0]
    #     robot_curr_col = self.grid.robot_location[1]
    #     while True:
    #         best_action, next_state = self.get_policy(
    #             robot_curr_row, robot_curr_col)
    #         self.update(robot_curr_row, robot_curr_col,
    #                     best_action, next_state.row, next_state.col)
    #         robot_curr_row = next_state.row
    #         robot_curr_col = next_state.col
    #         if best_action == Action.exit_game:
    #             break

    def get_policy(self, row, col):
        state = self.grid.states[row][col]
        possible_states = self.grid.find_possible_states(row, col)
        exploration_action = random.choice(list(possible_states.keys()))
        exploration_state = possible_states[exploration_action]

        if random.random() < self.noise:
            return exploration_action, exploration_state

        max_q_value = float('-inf')
        best_actions = []
        for action, value in state.q_values.items():
            if value > max_q_value:
                best_actions = [action]
                max_q_value = value
            elif value == max_q_value:
                best_actions.append(action)

        best_random_action = random.choice(best_actions)
        dest_state = possible_states[best_random_action]

        return best_random_action, dest_state

    def q_learn(self):
        best_action, next_state = self.get_policy(
            self.grid.robot_curr_location[0], self.grid.robot_curr_location[1])
        self.update(self.grid.robot_curr_location[0], self.grid.robot_curr_location[1],
                    best_action, next_state.row, next_state.col)
        self.grid.robot_curr_location[0] = next_state.row
        self.grid.robot_curr_location[1] = next_state.col
        if best_action == Action.exit_game:
            self.grid.robot_curr_location = self.grid.robot_start_location[:]
            self.episodes += 1
            return
