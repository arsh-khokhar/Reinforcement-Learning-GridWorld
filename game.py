import pygame, sys
from enum import IntEnum
from pygame.locals import *

from visualizer import Visualizer
from visualizer import State

class Game:
    def __init__(self, window_width: int, window_height: int, input_vs: Visualizer) -> None:    
        # Initialise screen
        pygame.display.set_caption('Grid World')

        self.background_color = (0, 0, 0)
        self.color = (150, 150, 150)

        self.background = pygame.display.set_mode((window_width, window_height))
        self.background.fill(self.background_color)
        
        self.window_width = window_width
        self.window_height = window_height

        self.vs = input_vs

        self.num_rows = len(input_vs.grid)
        self.num_cols = len(input_vs.grid[0])
        self.cell_size = window_height // self.num_rows

        self.grid_rect = pygame.Surface((self.cell_size*self.num_rows, self.cell_size*self.num_cols))
        #self.grid_rect.blit(robot_img, pygame.Rect((input_vs.robot_pos[0])*self.cell_size, (input_vs.robot_pos[1])*self.cell_size, self.cell_size, self.cell_size))
        # Fate: 0, Fate: Stay night
    def clear(self):
        self.background.fill((0,0,0))
        self.grid_rect.fill((0,0,0))
    
    def draw_static(self):
        boulder_img = pygame.image.load('./boulder.png')   
        boulder_img = pygame.transform.scale(boulder_img, (int(self.cell_size), int(self.cell_size)*boulder_img.get_height()//boulder_img.get_width()))

        firepit_img = pygame.image.load('./fire.png') 
        firepit_img = pygame.transform.scale(firepit_img, (int(self.cell_size), int(self.cell_size)*firepit_img.get_height()//firepit_img.get_width()))

        diamond_img = pygame.image.load('./diamond.png') 
        diamond_img = pygame.transform.scale(diamond_img, (int(self.cell_size), int(self.cell_size)*diamond_img.get_height()//diamond_img.get_width()))

        for i, row in enumerate(self.vs.grid):
            for j, cell in enumerate(row):
                rect = pygame.Rect(i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.grid_rect, self.background_color, rect)
                pygame.draw.rect(self.grid_rect, self.color, rect, 1)
                if cell["type"] == State.TERMINAL:
                    self.grid_rect.blit(diamond_img, rect)
                elif cell["type"] == State.BOULDER:
                    self.grid_rect.blit(boulder_img, rect)
                elif cell["type"] == State.FIRE_PIT:
                    self.grid_rect.blit(firepit_img, rect)
    
    def display(self) -> None:
        pygame.init()

        robot_img = pygame.image.load('./robot.png')   
        robot_img = pygame.transform.scale(robot_img, (int(self.cell_size), int(self.cell_size)*robot_img.get_height()//robot_img.get_width()))

        font = pygame.font.Font('freesansbold.ttf', 32)
 
        # create a text suface object,
        # on which text is drawn on it.
        text = font.render('Value After N Iterations', True, (255,255,255))
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (self.window_width // 2, int(self.grid_rect.get_height()*1.2))
        
        while True:
            self.clear()
            self.draw_static()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    last_pos_hor = self.vs.robot_pos[0]
                    last_pos_vert = self.vs.robot_pos[1]
                    if event.key == K_w:
                        self.vs.move_robot(last_pos_hor, last_pos_vert, last_pos_hor, last_pos_vert-1)
                    elif event.key == K_s:
                        self.vs.move_robot(last_pos_hor, last_pos_vert, last_pos_hor, last_pos_vert+1)
                    elif event.key == K_a:
                        self.vs.move_robot(last_pos_hor, last_pos_vert, last_pos_hor-1, last_pos_vert)
                    elif event.key == K_d:
                        self.vs.move_robot(last_pos_hor, last_pos_vert, last_pos_hor+1, last_pos_vert)
            self.grid_rect.blit(robot_img, pygame.Rect((self.vs.robot_pos[0])*self.cell_size, (self.vs.robot_pos[1])*self.cell_size, self.cell_size, self.cell_size))
            self.background.blit(self.grid_rect, (self.window_width //2 - self.grid_rect.get_width() // 2, self.window_height*0.05))
            self.background.blit(text, textRect)
            pygame.display.update()

def main():
    #game.display()
    size = 1000
    grid_rows = 5
    grid_cols = 8
    vs = Visualizer()
    vs.initialize_grid(grid_cols, grid_rows, 4, 0.1)
    vs.set_state_type(1,1, State.BOULDER)
    vs.set_state_type(3,0, State.TERMINAL)
    vs.set_state_type(3,1, State.FIRE_PIT)
    vs.put_robot_at(0, 2)
    game = Game(int(size*grid_cols // grid_rows), size, vs)
    game.display()

if __name__ == '__main__': main()