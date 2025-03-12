# game.py
import pygame
from config import *
from Pancake import Pancake
from player import Player
from ui import draw_pancakes, draw_plate, draw_scores

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pancake Dragging Prototype")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.pancakes = [
            Pancake(INITIAL_PANCAKE_POS[0], "regular"),
            Pancake(INITIAL_PANCAKE_POS[1], "star"),
            Pancake(INITIAL_PANCAKE_POS[2], "regular")
        ]
        self.players = [Player("Player 1"), Player("Player 2")]
        self.running = True
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for pancake in self.pancakes:
                pancake.handle_event(event)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_plate(self.screen)
        draw_pancakes(self.screen, self.pancakes)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()