import pygame
import sys
from enum import Enum
from pygame.locals import *
from value_iteration import *


class GridColours(Enum):
    white = (255, 255, 255)
    grey = (150, 150, 150)
    black = (0, 0, 0)
    blue = (0, 0, 255)


class Visualizer:
    def __init__(self, cell_size: int, num_rows, num_columns) -> None:
        # Initialise screen
        pygame.display.set_caption('Grid world')

        self.num_rows = num_rows
        self.num_cols = num_columns

        self.cell_size = cell_size
        self.font_size = self.cell_size // 5

        self.grid_width = cell_size * self.num_cols
        self.grid_height = cell_size * self.num_rows
        self.window_width = self.grid_width + 150
        self.window_height = self.grid_height + 150

        self.background = pygame.display.set_mode(
            (self.window_width, self.window_height))

        self.grid_rect = pygame.Surface((self.grid_width, self.grid_height))
        self.grid_rect.get_rect().center = (self.window_width // 2, 0)

    def clear(self):
        self.background.fill(GridColours.black.value)
        self.grid_rect.fill(GridColours.black.value)

    def draw_values(self):
        font = pygame.font.SysFont(
            'courier new', self.font_size, bold=True)
        for j, row in enumerate(x.states):
            for i, state in enumerate(row):
                rect = pygame.Rect(
                    i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)
                color = (int(180*abs(state.value) / x.max_terminal_val), 0,
                         0) if state.value < 0 else (0, int(180*abs(state.value) / x.max_terminal_val), 0)
                pygame.draw.rect(self.grid_rect, color, rect)
                pygame.draw.rect(
                    self.grid_rect, GridColours.white.value, rect, 1)

                if state.is_boulder:
                    pygame.draw.rect(
                        self.grid_rect, GridColours.grey.value, rect)
                    continue

                if state.is_terminal:
                    inner_rect = pygame.Rect(
                        i*self.cell_size + self.cell_size*0.1,
                        j*self.cell_size + self.cell_size*0.1,
                        self.cell_size*0.8, self.cell_size*0.8)
                    pygame.draw.rect(
                        self.grid_rect, GridColours.white.value, inner_rect, 1)

                value_text = font.render('{:.2f}'.format(state.value),
                                         True, GridColours.white.value)
                value_rect = value_text.get_rect()
                value_rect.center = (i*self.cell_size + self.cell_size // 2,
                                     j*self.cell_size + self.cell_size // 2)
                self.grid_rect.blit(value_text, value_rect)

                if state.is_terminal:
                    continue

                dir_text = None
                dir_center = None

                if state.best_action == Action.north:
                    dir_text = '▲'
                    dir_center = (i + 0.5)*self.cell_size, j * \
                        self.cell_size + self.font_size*0.5

                elif state.best_action == Action.east:
                    dir_text = '►'
                    dir_center = (i+1)*self.cell_size - \
                        self.font_size*0.5, (j+0.5)*self.cell_size

                elif state.best_action == Action.west:
                    dir_text = '◄'
                    dir_center = i*self.cell_size + \
                        self.font_size*0.5, (j+0.5)*self.cell_size

                elif state.best_action == Action.south:
                    dir_text = '▼'
                    dir_center = (i+0.5)*self.cell_size, (j+1) * \
                        self.cell_size - self.font_size*0.5

                if dir_text and dir_center:
                    dir_render_text = font.render(
                        dir_text, True, GridColours.white.value)
                    dir_rect = dir_render_text.get_rect()
                    dir_rect.center = (dir_center[0], dir_center[1])
                    self.grid_rect.blit(dir_render_text, dir_rect)

    def draw_q_val_triangle(self, points, value, centers, text_color):
        font = pygame.font.SysFont(
            'courier new', int(self.font_size*0.65), bold=True)
        normalized = int(180*abs(value) / x.max_terminal_val)
        color = (normalized, 0, 0) if value < 0 else (0, normalized, 0)
        pygame.draw.polygon(
            self.grid_rect, color, points)
        pygame.draw.polygon(
            self.grid_rect, GridColours.white.value, points, 1)
        q_val_text = font.render('{:.2f}'.format(
            value), True, text_color)
        q_val_rect = q_val_text.get_rect()
        q_val_rect.center = (centers[0], centers[1])
        self.grid_rect.blit(q_val_text, q_val_rect)

    def draw_q_values(self):
        for j, row in enumerate(x.states):
            for i, state in enumerate(row):
                rect = pygame.Rect(
                    i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)

                if state.is_boulder:
                    pygame.draw.rect(
                        self.grid_rect, GridColours.grey.value, rect)
                    continue

                top_left = (i*self.cell_size, j*self.cell_size)
                top_right = ((i+1)*self.cell_size, j*self.cell_size)
                bottom_left = (i*self.cell_size, (j+1)*self.cell_size)
                bottom_right = ((i+1)*self.cell_size, (j+1)*self.cell_size)
                mid = ((i + 0.5)*self.cell_size, (j + 0.5)*self.cell_size)

                for q_value_key in state.q_values:
                    q_value = state.q_values[q_value_key]
                    text_color = GridColours.white.value if q_value_key == state.best_action \
                        else GridColours.grey.value

                    if q_value_key == Action.north:
                        self.draw_q_val_triangle(
                            [top_left, top_right, mid], q_value,
                            [mid[0], top_left[1] + self.font_size // 2], text_color)

                    elif q_value_key == Action.east:
                        self.draw_q_val_triangle(
                            [top_right, bottom_right, mid], q_value,
                            [bottom_right[0] - self.font_size, mid[1]], text_color)

                    elif q_value_key == Action.west:
                        self.draw_q_val_triangle(
                            [top_left, bottom_left, mid], q_value,
                            [bottom_left[0] + self.font_size, mid[1]], text_color)

                    if q_value_key == Action.south:
                        self.draw_q_val_triangle(
                            [bottom_left, bottom_right, mid], q_value,
                            [mid[0], bottom_left[1] - self.font_size // 2], text_color)

                    if q_value_key == Action.exit_game:
                        font = pygame.font.SysFont(
                            'courier new', int(self.font_size), bold=True)
                        normalized = int(180*abs(q_value) / x.max_terminal_val)
                        color = (normalized, 0, 0) if q_value < 0 else (
                            0, normalized, 0)
                        q_val_text = font.render('{:.2f}'.format(
                            q_value), True, GridColours.white.value)
                        q_val_rect = q_val_text.get_rect()
                        q_val_rect.center = (mid[0], mid[1])
                        pygame.draw.rect(
                            self.grid_rect, color, rect)
                        self.grid_rect.blit(q_val_text, q_val_rect)
                        inner_rect = pygame.Rect(
                            i*self.cell_size + self.cell_size*0.1, j*self.cell_size + self.cell_size*0.1,
                            self.cell_size*0.8, self.cell_size*0.8)
                        pygame.draw.rect(
                            self.grid_rect, GridColours.white.value, inner_rect, 1)

                pygame.draw.rect(
                    self.grid_rect, GridColours.white.value, rect, 1)

    def display(self) -> None:
        pygame.init()
        k = 0
        text_to_show = "VALUES AFTER {} ITERATIONS"
        to_draw_ptr = self.draw_q_values
        robot_row = 2
        robot_col = 0
        while True:
            self.clear()
            to_draw_ptr()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_w:
                        action = Action.north
                        if robot_row - 1 >= 0:
                            x.update(robot_row, robot_col, action,
                                     robot_row-1, robot_col)
                            robot_row -= 1

                    if event.key == K_s:
                        action = Action.south
                        if robot_row + 1 < self.num_rows:
                            x.update(robot_row, robot_col, action,
                                     robot_row+1, robot_col)
                            robot_row += 1

                    if event.key == K_d:
                        action = Action.east
                        if robot_col + 1 < self.num_cols:
                            x.update(robot_row, robot_col, action,
                                     robot_row, robot_col+1)
                            robot_col += 1

                    if event.key == K_a:
                        action = Action.west
                        if robot_col - 1 >= 0:
                            x.update(robot_row, robot_col, action,
                                     robot_row, robot_col-1)
                            robot_col -= 1

                    if event.key == K_e:
                        action = Action.exit_game
                        x.update(robot_row, robot_col, action,
                                 robot_row, robot_col)
                        robot_row = 2
                        robot_col = 0

                    if event.key == K_SPACE:
                        to_draw_ptr = self.draw_q_values if to_draw_ptr == self.draw_values else self.draw_values
                        text_to_show = "Q-VALUES AFTER {} ITERATIONS" if to_draw_ptr == self.draw_q_values \
                            else "VALUES AFTER {} ITERATIONS"
            pygame.draw.circle(self.grid_rect, GridColours.blue.value,
                               ((robot_col+0.5)*self.cell_size, (robot_row+0.5)*self.cell_size), 0.125*self.cell_size)
            font = pygame.font.SysFont(
                'courier new', 50, bold=True)
            iteration_text = font.render(text_to_show.format(
                k), True, GridColours.white.value)
            iteration_rect = iteration_text.get_rect()
            iteration_rect.center = (
                self.window_width // 2, self.window_height - 50)
            self.background.blit(
                self.grid_rect, (self.window_width // 2 - self.grid_width // 2, 50))
            self.background.blit(iteration_text, iteration_rect)
            pygame.display.update()


if __name__ == '__main__':
    x = Grid()
    x.load_from_file("gridConf_default.txt")

    cell_size = 1000 // max(x.grid_size["vertical"], x.grid_size["horizontal"])

    game = Visualizer(
        cell_size, x.grid_size["vertical"], x.grid_size["horizontal"])

    game.display()
