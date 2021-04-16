"""
    File name: q_learning_agent.py
    Author: Arsh Khokhar, Kiernan Wiese
    Date last modified: 15 April, 2021
    Python Version: 3.8

    This script contains the QLearningAgent class used to run q learning.
"""
import random
from grid import Grid, Action


class QLearningAgent:
    """
    Representation of a QLearningAgent
    Attributes
        grid                The grid that the agent will be working with when learning
        discount            The discount value
        noise               The likelihood the robot won't end up where it's going
        alpha               The discount alpha
        max_display_val     TODO: again no idea what this does
        curr_episode        The number of the current episdoe
    """
    def __init__(self, input_grid: Grid):
        """
        Init function for the QLearningAgent class

        :param input_grid: The grid that the agent will be working with when learning
        """
        self.grid = input_grid
        self.discount = input_grid.discount
        self.noise = input_grid.noise
        self.alpha = input_grid.alpha
        self.max_display_val = input_grid.max_terminal_val
        self.curr_episode = 0

    def find_max_q_value(self, row, col):
        """
        Get the highest q value for a given state

        :param row: The row of the state to check
        :param col: The column of the state to check
        :return: The max q value and the action to take to get it
        """
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
        """
        Update q values based on an action

        :param row: The row of the state to update
        :param col: The column of the state to update
        :param action: The action taken to end up at dest_row, dest_col
        :param dest_row: The row of the resulting state
        :param dest_col: The column of the resulting state
        :return: True if the move was a success, false otherwise
        """
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

    def get_policy(self, row, col):
        """
        Get the best action to be taken at a given state

        :param row: The row of the state to check
        :param col: The column of the state to check
        """
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
        """
        Call various other functions to run through 1 episode of q learning
        """
        best_action, next_state = self.get_policy(
            self.grid.robot_curr_location[0], self.grid.robot_curr_location[1])
        self.update(self.grid.robot_curr_location[0], self.grid.robot_curr_location[1],
                    best_action, next_state.row, next_state.col)
        self.grid.robot_curr_location[0] = next_state.row
        self.grid.robot_curr_location[1] = next_state.col
        if best_action == Action.exit_game:
            self.grid.robot_curr_location = self.grid.robot_start_location[:]
            self.curr_episode += 1
            return
