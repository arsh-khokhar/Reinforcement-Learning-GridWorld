from grid import Grid, Action, ACTION_NEIGHBOURS


class ValueIterationAgent:

    def __init__(self, input_grid: Grid):
        self.grid = input_grid
        self.discount = input_grid.discount
        self.noise = input_grid.noise
        self.max_display_val = input_grid.max_terminal_val

    def iterate_value(self, row, col):
        state = self.grid.states[row][col]
        if state.is_terminal:
            state.q_values[Action.exit_game] = state.terminal_reward
            return
        possible_states = self.grid.find_possible_states(row, col)

        for action in state.get_actions():
            summation = 0.0
            summation += (1.0 - self.noise) * \
                (possible_states[action].reward +
                 self.grid.discount*possible_states[action].value)

            for neighbour in ACTION_NEIGHBOURS[action]:
                summation += (self.noise / 2.0) * (
                    possible_states[neighbour].reward + self.discount*possible_states[neighbour].value)

            state.q_values[action] = summation

    def update_values(self):
        # updating the values
        for row in self.grid.states:
            for state in row:
                if not state.is_boulder:
                    best_action = None
                    max_q_value = float('-inf')
                    for key in state.q_values:
                        if state.q_values[key] > max_q_value:
                            max_q_value = state.q_values[key]
                            best_action = key
                        if self.max_display_val < abs(state.q_values[key]):
                            self.max_display_val = abs(state.q_values[key])
                    state.value = max_q_value
                    state.best_action = best_action

    def iterate_values(self, k):
        for i, row in enumerate(self.grid.states):
            for j, state in enumerate(row):
                if not state.is_boulder:
                    self.iterate_value(i, j)
        self.update_values()
