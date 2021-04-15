from grid import Grid
from visualizer import Visualizer
from value_iteration_agent import ValueIterationAgent
from q_learning_agent import QLearningAgent
from copy import deepcopy


def load_results(filename):
    mdp_results = {}
    rl_results = {}
    with open(filename, 'r') as fp:
        lines = fp.readlines()

    for line in lines:
        row, col, number, learning_type, query = line.strip().split(',')
        row, col, number = int(row), int(col), int(number)
        new_elem_dict = {"row": row, "col": col, "query": query}
        if learning_type.lower() == 'mdp':
            if number in mdp_results:
                mdp_results[number].append(new_elem_dict)
            else:
                mdp_results[number] = [new_elem_dict]
        elif learning_type.lower() == 'rl':
            if number in rl_results:
                rl_results[number].append(new_elem_dict)
            else:
                rl_results[number] = [new_elem_dict]

    return mdp_results, rl_results


mdp_grid = Grid()
rl_grid = Grid()

result_mdp_grids = {}
result_rl_grids = {}

file_name = "gridConf.txt"

mdp_grid.load_from_file(file_name)
rl_grid.load_from_file(file_name)

mdp_test, rl_test = load_results("results.txt")

value_iter_agent = ValueIterationAgent(mdp_grid)

q_learn_agent = QLearningAgent(rl_grid)

cell_size = 600 // max(mdp_grid.num_rows, mdp_grid.num_cols)

for i in range(mdp_grid.k):
    value_iter_agent.iterate_values(0)
    if i in mdp_test:
        result_mdp_grids[i] = deepcopy(value_iter_agent)

print("value iter done")

while q_learn_agent.episodes < 3500:
    q_learn_agent.q_learn()
    if q_learn_agent.episodes in rl_test:
        result_rl_grids[i] = deepcopy(q_learn_agent)


print("q learning done")


for result in result_mdp_grids:
    print(result)
    result_mdp_grids[result].grid.print_states()

    # game = Visualizer(cell_size, result_mdp_grids[result])
    # game.display()

# game = Visualizer(
#     cell_size, value_iter_agent)

# game.display()

# print("DONE!!! game 1")

# game2 = Visualizer(
#     cell_size, q_learn_agent)
# game2.display()
