import pygame
from config import *
from cookie import Pancake
# from player import Player  # Not used in this prototype
from ui import draw_pancakes, draw_plate  # draw_scores removed for now

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pancake Dragging Game")
        self.clock = pygame.time.Clock()
        
        # Initialize pancakes (stack order from bottom to top)
        self.pancakes = [
            Pancake((400, 500), 'regular'),
            Pancake((400, 450), 'star'),
            Pancake((400, 400), 'regular')
        ]
        self.dragging_pancake = None
        self.running = True
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Check pancakes in reverse so the top pancake is selected first
                for pancake in reversed(self.pancakes):
                    if pancake.is_clicked(pos):
                        pancake.dragging = True
                        pancake.offset_x = pancake.position[0] - pos[0]
                        pancake.offset_y = pancake.position[1] - pos[1]
                        self.dragging_pancake = pancake
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_pancake:
                    self.dragging_pancake.dragging = False
                    self.dragging_pancake = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_pancake and self.dragging_pancake.dragging:
                    pos = pygame.mouse.get_pos()
                    new_x = pos[0] + self.dragging_pancake.offset_x
                    new_y = pos[1] + self.dragging_pancake.offset_y
                    self.dragging_pancake.position = (new_x, new_y)
    
    def update(self):
        # No update logic for this drag/drop prototype
        pass
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_plate(self.screen)
        draw_pancakes(self.screen, self.pancakes)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()