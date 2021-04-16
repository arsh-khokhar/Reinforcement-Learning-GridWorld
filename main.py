"""
    File name: main.py
    Author: Arsh Khokhar, Kiernan Wiese
    Date last modified: 15 April, 2021
    Python Version: 3.8

    This script contains the main function that calls both of the agent
    scripts to do either value iteration or q learning based on data it reads
    from gridConf.txt and results.txt.
"""
from grid import Grid
from visualizer import Visualizer
from value_iteration_agent import ValueIterationAgent
from q_learning_agent import QLearningAgent
from copy import deepcopy


def load_results(filename: str):
    """
    :param filename: The name of the results file to load (results.txt)
    :return: Two dictionaries containing representations of the queries the input file
    """
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


def main():
    file_name = "gridConf.txt"
    mdp_grid = Grid(file_name)
    rl_grid = Grid(file_name)

    result_mdp_grids = {}
    result_rl_grids = {}

    mdp_queries, rl_queries = load_results("results.txt")

    value_iter_agent = ValueIterationAgent(mdp_grid)

    q_learn_agent = QLearningAgent(rl_grid)

    cell_size = 600 // max(mdp_grid.num_rows, mdp_grid.num_cols)

    for i in range(mdp_grid.k):
        value_iter_agent.iterate_values()
        if i in mdp_queries:
            result_mdp_grids[i] = deepcopy(value_iter_agent)

    print("value iter done")

    while q_learn_agent.curr_episode < 3500:
        q_learn_agent.q_learn()
        if q_learn_agent.curr_episode in rl_queries:
            result_rl_grids[q_learn_agent.curr_episode] = deepcopy(q_learn_agent)

    print("q learning done")

    for episode in mdp_queries:
        for row, col, query in mdp_queries[episode]:
            game = Visualizer(cell_size, result_mdp_grids[episode])
            game.display()

    for episode in rl_queries:
        for row, col, query in rl_queries[episode]:
            game = Visualizer(cell_size, result_rl_grids[episode])
            game.display()


if __name__ == '__main__':
    main()
