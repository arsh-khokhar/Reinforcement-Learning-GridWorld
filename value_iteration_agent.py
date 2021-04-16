"""
    File name: value_iteration_agent.py
    Author: Arsh Khokhar, Kiernan Wiese
    Date last modified: 15 April, 2021
    Python Version: 3.8

    This script contains the ValueIterationAgent class used to run value
    iteration.
"""
from grid import Grid, Action, ACTION_NEIGHBOURS


class ValueIterationAgent:
    """
    Representation of a ValueIterationAgent
    Attributes
        grid                The grid that the agent will be working with when learning
        discount            The discount value
        noise               The likelihood the robot won't end up where it's going
        max_display_val     keeps track of the maximum terminal value for 
                            darker/lighter GUI colors
    """

    def __init__(self, input_grid: Grid):
        """
        Init function for the ValueIterationAgent class

        :param input_grid: The grid that the agent will be working with when learning
        """
        self.grid = input_grid
        self.discount = input_grid.discount
        self.noise = input_grid.noise
        self.max_display_val = self.grid.max_terminal_val
        self.curr_iteration = 0

    def iterate_value(self, row, col):
        """
        Update the q values of the state at row, col

        :param row: The row of the state to iterate
        :param col: The column of the state to iterate
        """
        state = self.grid.states[row][col]
        if state.is_terminal:
            state.q_values[Action.exit_game] = state.terminal_reward
            return
        possible_states = self.grid.find_possible_states(row, col)

        for action in state.get_actions():
            summation = 0.0
            summation += (1.0 - self.noise) * \
                (possible_states[action].reward +
                 self.grid.discount * possible_states[action].max_q_value)

            for neighbour in ACTION_NEIGHBOURS[action]:
                summation += (self.noise / 2.0) * (
                    possible_states[neighbour].reward + self.discount*possible_states[neighbour].max_q_value)

            state.q_values[action] = summation

    def update_values(self):
        """
        Set the best value and action for each state in the grid based on its
        update q values
        """
        for row in self.grid.states:
            for state in row:
                if not state.is_boulder:
                    best_action = None
                    max_q_value = float('-inf')
                    for key in state.q_values:
                        if state.q_values[key] > max_q_value:
                            max_q_value = state.q_values[key]
                            best_action = key
                    state.max_q_value = max_q_value
                    state.best_action = best_action

    def iterate_values(self):
        """
        Call various other functions to run through 1 step of value iteration
        """
        for i, row in enumerate(self.grid.states):
            for j, state in enumerate(row):
                if not state.is_boulder:
                    self.iterate_value(i, j)
        self.update_values()
        self.curr_iteration += 1

    def get_display_index(self):
        return self.curr_iteration
