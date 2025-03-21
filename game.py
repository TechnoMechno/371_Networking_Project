# game.py
import pygame
from config import *
from cookie import Cookie  # Changed from pancake import
from player import Player
from ui import draw_cookies, draw_plate  # Changed from draw_pancakes
from Plate import Plate

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cookie Dragging Prototype")  # Changed title
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.cookies = [
            Cookie(INITIAL_COOKIE_POS[0], "regular"),
            Cookie(INITIAL_COOKIE_POS[1], "star"),
            Cookie(INITIAL_COOKIE_POS[2], "regular")
        ]
        self.players = [Player("Player 1"), Player("Player 2")]
        self.running = True
        self.central_plate = Plate(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 260)
    
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
            for cookie in self.cookies:
                cookie.handle_event(event)
    
    def draw(self):
        
        self.screen.fill(BACKGROUND_COLOR)
        self.central_plate.draw(self.screen)
        draw_cookies(self.screen, self.cookies)
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()