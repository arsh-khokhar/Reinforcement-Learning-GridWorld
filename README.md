### Authors: Arsh Khokhar (7833350), Kiernan Wiese (7813635)

### Requirements

First, you'll need to install the requirements. To do so, use `pip install -r requirements.txt`

### Running the program

To run the program with default files (gridConf.txt) and (results.txt), use `python main.py`.
This will run all of the episodes and iterations for both q learning and value iteration.
Afterwards it will open up all of the gui windows, showing the answer to each of the queries in results.txt one by one.
To go from one query to the next, close the current gui window. This will open another gui window, with the next query.

### Optional arguments

With the command `python main.py`, you can use the following arguments for loading custom grid file, custom results file or launching interactive agents.

- -h, --help show this help message and exit
- --interactive_rl Launch interactive reinforcement learning grid
- --interactive_mdp Launch interactive MDP grid
- --grid GRID Use a custom grid file
- --results RESULTS Use a custom result file

A sample command with interactive Reinforcement learning grid and custom files: `python main.py --interactive_rl --grid=customGrid.txt --results=customResults.txt`

### Controls for interactive grids

#### MDP

- V: iterate values for one more iteration
- SPACE: toggle between displaying values and q-values

#### Reinforcement learning

- W: Move the robot up
- S: Move the robot down
- A: Move the robot left
- D: Move the robot right
- E: Take the exit action (only works at terminal states)
