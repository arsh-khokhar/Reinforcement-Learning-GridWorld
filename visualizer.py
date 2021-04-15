import pygame
import sys
from enum import Enum
from pygame.locals import *
from grid import Grid, Action
from value_iteration_agent import ValueIterationAgent
from q_learning_agent import QLearningAgent


class GridColours(Enum):
    white = (255, 255, 255)
    grey = (150, 150, 150)
    black = (0, 0, 0)
    blue = (0, 0, 255)


class Visualizer:

    def __init__(self, cell_size: int, agent, is_interactive=False) -> None:
        # Initialise screen
        pygame.display.set_caption('Grid world')
        self.is_interactive = is_interactive
        self.agent = agent
        self.value_iter_bool = True if type(
            agent) is ValueIterationAgent else False
        self.num_rows = agent.grid.num_rows
        self.num_cols = agent.grid.num_cols

        self.cell_width = cell_size
        self.cell_size = cell_size
        self.font = 'courier new'
        self.font_size = int(self.cell_width // 5)

        self.grid_width = self.cell_width * self.num_cols
        self.grid_height = self.cell_size * self.num_rows
        self.window_width = self.grid_width + 150
        self.window_height = self.grid_height + 200

        self.background = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE)

        self.grid_rect = pygame.Surface((self.grid_width, self.grid_height))

        self.q_val_grid_rect = pygame.Surface(
            (self.grid_width, self.grid_height))

        self.grid_rect.get_rect().center = (self.window_width // 2, 0)
        self.q_val_grid_rect.get_rect().center = (self.window_width // 2, 0)

    def clear(self):
        self.background.fill(GridColours.black.value)
        self.grid_rect.fill(GridColours.black.value)

    def draw_values(self):
        font = pygame.font.SysFont(
            self.font, self.font_size, bold=True)
        for j, row in enumerate(self.agent.grid.states):
            for i, state in enumerate(row):
                rect = pygame.Rect(
                    i*self.cell_width, j*self.cell_size, self.cell_width, self.cell_size)
                color = (int(180*abs(state.value) / self.agent.max_display_val), 0,
                         0) if state.value < 0 else (0, int(180*abs(state.value) / self.agent.max_display_val), 0)
                pygame.draw.rect(self.grid_rect, color, rect)
                pygame.draw.rect(
                    self.grid_rect, GridColours.white.value, rect, 1)

                if state.is_boulder:
                    pygame.draw.rect(
                        self.grid_rect, GridColours.grey.value, rect)
                    continue

                if state.is_terminal:
                    inner_rect = pygame.Rect(
                        i*self.cell_width + self.cell_width*0.1,
                        j*self.cell_size + self.cell_size*0.1,
                        self.cell_width*0.8, self.cell_size*0.8)
                    pygame.draw.rect(
                        self.grid_rect, GridColours.white.value, inner_rect, 1)

                value_text = font.render('{:.2f}'.format(state.value),
                                         True, GridColours.white.value)
                value_rect = value_text.get_rect()
                value_rect.center = (i*self.cell_width + self.cell_width // 2,
                                     j*self.cell_size + self.cell_size // 2)
                value_text = pygame.transform.flip(value_text, False, True)
                self.grid_rect.blit(value_text, value_rect)

                if state.is_terminal:
                    continue

                dir_text = None
                dir_center = None

                if state.best_action == Action.north:
                    dir_text = '▲'
                    dir_center = (i + 0.5)*self.cell_width, (j+1) * \
                        self.cell_size - self.font_size*0.5

                elif state.best_action == Action.east:
                    dir_text = '►'
                    dir_center = (i+1)*self.cell_width - \
                        self.font_size*0.5, (j+0.5)*self.cell_size

                elif state.best_action == Action.west:
                    dir_text = '◄'
                    dir_center = i*self.cell_width + \
                        self.font_size*0.5, (j+0.5)*self.cell_size

                elif state.best_action == Action.south:
                    dir_text = '▼'
                    dir_center = (i+0.5)*self.cell_width, j * \
                        self.cell_size + self.font_size*0.5

                if dir_text and dir_center:
                    dir_render_text = font.render(
                        dir_text, True, GridColours.white.value)
                    dir_rect = dir_render_text.get_rect()
                    dir_render_text = pygame.transform.flip(
                        dir_render_text, False, True)
                    dir_rect.center = (dir_center[0], dir_center[1])
                    self.grid_rect.blit(dir_render_text, dir_rect)

    def draw_q_val_triangle(self, points, value, centers, text_color):
        font = pygame.font.SysFont(
            self.font, int(self.font_size*0.65), bold=True)
        normalized = int(180*abs(value) / self.agent.max_display_val)
        color = (normalized, 0, 0) if value < 0 else (0, normalized, 0)
        pygame.draw.polygon(
            self.grid_rect, color, points)
        pygame.draw.polygon(
            self.grid_rect, GridColours.white.value, points, 1)
        q_val_text = font.render('{:.2f}'.format(
            value), True, text_color)
        q_val_rect = q_val_text.get_rect()
        q_val_text = pygame.transform.flip(q_val_text, False, True)
        q_val_rect.center = (centers[0], centers[1])
        self.grid_rect.blit(q_val_text, q_val_rect)

    def draw_q_value_grid(self):
        for j, row in enumerate(self.agent.grid.states):
            for i, state in enumerate(row):
                rect = pygame.Rect(
                    i*self.cell_width, j*self.cell_size, self.cell_width, self.cell_size)

                if state.is_boulder:
                    pygame.draw.rect(
                        self.grid_rect, GridColours.grey.value, rect)
                    continue

                top_left = (i*self.cell_width, j*self.cell_size)
                top_right = ((i+1)*self.cell_width, j*self.cell_size)
                bottom_left = (i*self.cell_width, (j+1)*self.cell_size)
                bottom_right = ((i+1)*self.cell_width, (j+1)*self.cell_size)
                mid = ((i + 0.5)*self.cell_width, (j + 0.5)*self.cell_size)

                for q_value_key in state.q_values:
                    q_value = state.q_values[q_value_key]
                    text_color = GridColours.white.value if q_value_key == state.best_action \
                        else GridColours.grey.value

                    if q_value_key == Action.south:
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

                    if q_value_key == Action.north:
                        self.draw_q_val_triangle(
                            [bottom_left, bottom_right, mid], q_value,
                            [mid[0], bottom_left[1] - self.font_size // 2], text_color)

                    if q_value_key == Action.exit_game:
                        font = pygame.font.SysFont(
                            self.font, self.font_size, bold=True)
                        normalized = int(180*abs(q_value) /
                                         self.agent.max_display_val)
                        color = (normalized, 0, 0) if q_value < 0 else (
                            0, normalized, 0)
                        q_val_text = font.render('{:.2f}'.format(
                            q_value), True, GridColours.white.value)
                        q_val_rect = q_val_text.get_rect()
                        q_val_rect.center = (mid[0], mid[1])
                        q_val_text = pygame.transform.flip(
                            q_val_text, False, True)
                        pygame.draw.rect(
                            self.grid_rect, color, rect)
                        self.grid_rect.blit(q_val_text, q_val_rect)
                        inner_rect = pygame.Rect(
                            i*self.cell_width + self.cell_width*0.1, j*self.cell_size + self.cell_size*0.1,
                            self.cell_width*0.8, self.cell_size*0.8)
                        pygame.draw.rect(
                            self.grid_rect, GridColours.white.value, inner_rect, 1)

                pygame.draw.rect(
                    self.grid_rect, GridColours.white.value, rect, 1)

    def draw_q_values(self):
        for j, row in enumerate(self.agent.grid.states):
            for i, state in enumerate(row):
                rect = pygame.Rect(
                    i*self.cell_width, j*self.cell_size, self.cell_width, self.cell_size)

                if state.is_boulder:
                    pygame.draw.rect(
                        self.grid_rect, GridColours.grey.value, rect)
                    continue

                top_left = (i*self.cell_width, j*self.cell_size)
                top_right = ((i+1)*self.cell_width, j*self.cell_size)
                bottom_left = (i*self.cell_width, (j+1)*self.cell_size)
                bottom_right = ((i+1)*self.cell_width, (j+1)*self.cell_size)
                mid = ((i + 0.5)*self.cell_width, (j + 0.5)*self.cell_size)

                for q_value_key in state.q_values:
                    q_value = state.q_values[q_value_key]
                    text_color = GridColours.white.value if q_value_key == state.best_action \
                        else GridColours.grey.value

                    if q_value_key == Action.south:
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

                    if q_value_key == Action.north:
                        self.draw_q_val_triangle(
                            [bottom_left, bottom_right, mid], q_value,
                            [mid[0], bottom_left[1] - self.font_size // 2], text_color)

                    if q_value_key == Action.exit_game:
                        font = pygame.font.SysFont(
                            self.font, self.font_size, bold=True)
                        normalized = int(180*abs(q_value) /
                                         self.agent.max_display_val)
                        color = (normalized, 0, 0) if q_value < 0 else (
                            0, normalized, 0)
                        q_val_text = font.render('{:.2f}'.format(
                            q_value), True, GridColours.white.value)
                        q_val_rect = q_val_text.get_rect()
                        q_val_rect.center = (mid[0], mid[1])
                        q_val_text = pygame.transform.flip(
                            q_val_text, False, True)
                        pygame.draw.rect(
                            self.grid_rect, color, rect)
                        self.grid_rect.blit(q_val_text, q_val_rect)
                        inner_rect = pygame.Rect(
                            i*self.cell_width + self.cell_width*0.1, j*self.cell_size + self.cell_size*0.1,
                            self.cell_width*0.8, self.cell_size*0.8)
                        pygame.draw.rect(
                            self.grid_rect, GridColours.white.value, inner_rect, 1)

                pygame.draw.rect(
                    self.grid_rect, GridColours.white.value, rect, 1)

    def display(self, snapshot=False) -> None:
        pygame.init()
        text_to_show = "VALUES AFTER {} ITERATIONS" if self.value_iter_bool else "Q-VALUES AFTER {} EPISODES"
        param_str = "Discount: {} Transition cost: {}".format(
            self.agent.grid.discount, self.agent.grid.transition_cost)
        param_str2 = "Noise: {}".format(self.agent.grid.noise)
        param_str2 += " Alpha: {}".format(
            self.agent.grid.alpha) if not self.value_iter_bool else ""
        to_draw_ptr = self.draw_values if self.value_iter_bool else self.draw_q_values

        while True:
            robot_row = self.agent.grid.robot_curr_location[0]
            robot_col = self.agent.grid.robot_curr_location[1]
            self.clear()
            to_draw_ptr()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.VIDEORESIZE:
                    # There's some code to add back window content here.
                    self.background = pygame.display.set_mode((event.w, event.h),
                                                              pygame.RESIZABLE)
                    self.cell_size = self.cell_size*event.h / self.window_height
                    self.cell_width = self.cell_width*event.w / self.window_width
                    self.grid_width = self.cell_width * self.num_cols
                    self.grid_height = self.cell_size * self.num_rows
                    self.window_width = self.grid_width + 150
                    self.window_height = self.grid_height + 150
                    self.grid_rect = pygame.Surface(
                        (self.grid_width, self.grid_height))
                    self.grid_rect.get_rect().center = (self.window_width // 2, 0)
                    self.font_size = int(self.cell_width // 5)

                if event.type == KEYDOWN and self.is_interactive:
                    if event.key == K_w and not self.value_iter_bool:
                        action = Action.north
                        self.agent.update(robot_row, robot_col, action,
                                          robot_row + 1, robot_col)

                    if event.key == K_s and not self.value_iter_bool:
                        action = Action.south
                        self.agent.update(robot_row, robot_col, action,
                                          robot_row - 1, robot_col)

                    if event.key == K_d and not self.value_iter_bool:
                        action = Action.east
                        self.agent.update(robot_row, robot_col, action,
                                          robot_row, robot_col + 1)

                    if event.key == K_a and not self.value_iter_bool:
                        action = Action.west
                        self.agent.update(robot_row, robot_col, action,
                                          robot_row, robot_col-1)

                    if event.key == K_e and not self.value_iter_bool:
                        action = Action.exit_game
                        self.agent.update(robot_row, robot_col, action,
                                          robot_row, robot_col)

                    if event.key == K_v and self.value_iter_bool:
                        k += 1
                        self.agent.iterate_values(0)

                    if event.key == K_q and not self.value_iter_bool:
                        k += 1
                        self.agent.q_learn()

                    if event.key == K_SPACE and self.value_iter_bool:
                        to_draw_ptr = self.draw_q_values if to_draw_ptr == self.draw_values else self.draw_values
                        text_to_show = "Q-VALUES AFTER {} ITERATIONS" if to_draw_ptr == self.draw_q_values \
                            else "VALUES AFTER {} ITERATIONS"

            if not self.value_iter_bool:
                pygame.draw.circle(self.grid_rect, GridColours.blue.value,
                                   ((robot_col+0.5)*self.cell_width,
                                    (robot_row+0.5)*self.cell_size),
                                   0.125*self.cell_size)
            font = pygame.font.SysFont(
                self.font, 28, bold=True)
            iteration_text = font.render(text_to_show.format(
                self.agent.grid.k), True, GridColours.white.value)
            iteration_rect = iteration_text.get_rect()
            iteration_rect.center = (
                self.window_width // 2, self.window_height - 90)

            param_text = font.render(param_str, True, GridColours.white.value)
            param_text2 = font.render(
                param_str2, True, GridColours.white.value)
            param_rect = param_text.get_rect()
            param_rect2 = param_text2.get_rect()
            param_rect.center = (
                self.window_width // 2, self.window_height - 90 + 30)
            param_rect2.center = (
                self.window_width // 2, self.window_height - 90 + 60)
            flipped = pygame.transform.flip(self.grid_rect, False, True)

            self.background.blit(
                flipped, (self.window_width // 2 - self.grid_width // 2, 50))

            self.background.blit(iteration_text, iteration_rect)
            self.background.blit(param_text, param_rect)
            self.background.blit(param_text2, param_rect2)
            pygame.display.update()
