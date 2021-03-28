from enum import IntEnum

class State(IntEnum):
    """
    IntEnum class to represent a State in the grid
    """
    ORDINAL = 0 
    BOULDER = 1
    TERMINAL = 2
    FIRE_PIT = 3

class Visualizer:

    def initialize_grid(self, num_hor_cells: int, num_vert_cells: int, action_size: int, value: float) -> None:
        self.action_size = action_size
        self.value = value
        self.grid = []
        self.grid_size = {"horizontal": num_hor_cells, "vertical": num_vert_cells}
        self.robot_pos = [-1, -1]

        for i in range(num_hor_cells):
            self.grid.append([])
            for j in range(num_vert_cells):
                self.grid[i].append({"value": 0.0, "type": State.ORDINAL}) #*num_vert_cells)
    
    def move_robot(self, start_hor_cell: int, start_vert_cell: int, end_hor_cell: int, end_vert_cell: int) -> bool:
        if start_hor_cell != end_hor_cell and start_vert_cell != end_vert_cell:
            print("cannot make diagonal moves!")
            return False
        
        if abs(start_hor_cell - end_hor_cell) != 1 and \
            abs(start_vert_cell - end_vert_cell) != 1:
            print("This did not work out")
            return True
        
        toRet = self.put_robot_at(end_hor_cell, end_vert_cell)
        
        return toRet
    
    def update_q_value(self, hor_cell: int, vert_cell: int, index: int, new_value: float) -> None:
        return
    
    def set_state_value(self, hor_cell: int, vert_cell: int, value: float) -> None:
        return
    
    def set_state_type(self, hor_cell: int, vert_cell: int, new_type: State) -> None:
        self.grid[hor_cell][vert_cell]["type"] = new_type
        return

    def print_grid(self):
        for row in self.grid:
            print(row)

    def put_robot_at(self, hor_cell: int, vert_cell: int) -> bool:
        if hor_cell < 0 or \
            hor_cell > self.grid_size["horizontal"] - 1 or \
            vert_cell < 0 or\
            vert_cell > self.grid_size["vertical"] - 1:
            return False

        if self.grid[hor_cell][vert_cell]["type"] == State.BOULDER:
            return False
        self.robot_pos = [hor_cell, vert_cell]
        return True

    def exit(self) -> bool:
        return False
