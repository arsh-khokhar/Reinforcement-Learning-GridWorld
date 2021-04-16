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
import argparse


def load_results(filename: str):
    """
    Load the results file

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
    parser = argparse.ArgumentParser(description='Grid world')

    parser.add_argument('--interactive_rl',
                        help='Launch interative reinforcement learning grid', default=False, action="store_true")

    parser.add_argument('--interactive_mdp',
                        help='Launch interative MDP grid', default=False, action="store_true")

    parser.add_argument(
        '--grid', help='Use a custom grid file', type=str)

    parser.add_argument(
        '--results', help='Use a custom result file', type=str)

    args = parser.parse_args()

    grid_file = "gridConf.txt" if not args.grid else args.grid
    result_file = "results.txt" if not args.results else args.results

    if args.interactive_mdp:
        # Launch an interactive mdp grid with value iteration agent
        mdp_grid = Grid(grid_file)
        interative_mdp_agent = ValueIterationAgent(mdp_grid)
        game = Visualizer(interative_mdp_agent, is_interactive=True)
        game.display()

    elif args.interactive_rl:
        # Launch an interactive reinforcement learning grid with Q-learning agent
        rl_grid = Grid(grid_file)
        interative_rl_agent = QLearningAgent(rl_grid)
        game = Visualizer(interative_rl_agent, is_interactive=True)
        game.display()

    else:
        mdp_grid = Grid(grid_file)
        rl_grid = Grid(grid_file)

        result_mdp_grids = {}
        result_rl_grids = {}

        mdp_queries, rl_queries = load_results(result_file)

        value_iter_agent = ValueIterationAgent(mdp_grid)

        q_learn_agent = QLearningAgent(rl_grid)

        for i in range(mdp_grid.iterations):
            if i in mdp_queries:
                # take a 'snapshot' of the agent state for a query
                result_mdp_grids[i] = deepcopy(value_iter_agent)
            value_iter_agent.iterate_values()

        print("\nValue iteration done for {} iterations".format(mdp_grid.iterations))

        while q_learn_agent.curr_episode < q_learn_agent.grid.episodes:
            q_learn_agent.q_learn()
            if q_learn_agent.curr_episode in rl_queries:
                # take a 'snapshot' of the state for a query
                result_rl_grids[q_learn_agent.curr_episode] = deepcopy(
                    q_learn_agent)

        print("\nQ-Learning done for {} episodes".format(q_learn_agent.grid.episodes))
        # Showing results for the MDP queries
        for episode in mdp_queries:
            for query_data in mdp_queries[episode]:
                game = Visualizer(result_mdp_grids[episode])
                game.display(highlight_cell=[
                    query_data['row'], query_data['col']], query=query_data['query'])

        # Showing results for the RL queries
        for episode in rl_queries:
            for query_data in rl_queries[episode]:
                game = Visualizer(result_rl_grids[episode])
                game.display(highlight_cell=[
                    query_data['row'], query_data['col']], query=query_data['query'])


if __name__ == '__main__':
    main()
