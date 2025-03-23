# game.py
import pygame
import math
import random
from config import *
from cookie import Cookie  # Changed from pancake import
from player import Player
from ui import draw_cookies, draw_plate, draw_interface  # Changed from draw_pancakes
from Plate import Plate

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cookie Dragging Prototype")  # Changed title
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.cookies = []
        num_cookies = 50  # You can adjust this number
        spread_radius = 150  # cookie spread
        
        # Calculate positions in a circle on the central plate
        for i in range(num_cookies):
            angle = 2 * math.pi * i / num_cookies
            radius = spread_radius  # Distance from center of plate
            r = radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            
            # Position cookies in random positions on the central plate
            self.central_plate = Plate(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 260)
            
            x = self.central_plate.x + r * math.cos(theta)
            y = self.central_plate.y + r * math.sin(theta)
            
            # Alternate between regular and star cookies
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies.append(Cookie([x, y], cookie_type))

        self.players = [
            Player("Player 1"),
            Player("Player 2"),
            Player("Player 3"),
            Player("Player 4")
        ]
        
        # Create player plates at corners
        plate_radius = 150 
        margin = 30
        self.player_plates = [
            # Top-left corner (Player 1)
            Plate(margin + plate_radius, margin + plate_radius, plate_radius),
            # Top-right corner (Player 2)
            Plate(SCREEN_WIDTH - margin - plate_radius, margin + plate_radius, plate_radius),
            # Bottom-left corner (Player 3)
            Plate(margin + plate_radius, SCREEN_HEIGHT - margin - plate_radius, plate_radius),
            # Bottom-right corner (Player 4)
            Plate(SCREEN_WIDTH - margin - plate_radius, SCREEN_HEIGHT - margin - plate_radius, plate_radius)
        ]

        self.running = True
        self.game_over = False
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if not self.game_over:
                for cookie in reversed(self.cookies):
                    cookie.handle_event(event, self.player_plates, self.players)

    def update(self):
        # Check if all cookies are no longer on the central plate
        if not self.game_over:
            cookies_on_central = False
            cookies_on_player_plates = 0
            
            for cookie in self.cookies:
                # Check if the cookie is on the central plate
                if (abs(cookie.position[0] - self.central_plate.x) < self.central_plate.radius and 
                    abs(cookie.position[1] - self.central_plate.y) < self.central_plate.radius):
                    cookies_on_central = True
                
                # Count cookies on player plates
                for plate in self.player_plates:
                    if cookie.on_plate == plate:
                        cookies_on_player_plates += 1
            
            if not cookies_on_central and cookies_on_player_plates == len(self.cookies):
                self.game_over = True
    
    def draw(self):
        
        self.screen.fill(BACKGROUND_COLOR)
        self.central_plate.draw(self.screen)
        for plate in self.player_plates:
            plate.draw(self.screen)

        draw_cookies(self.screen, self.cookies)
        draw_interface(self.screen, self.players, self.player_plates)
        if self.game_over:
            self.draw_scoreboard()
        pygame.display.flip()

    def draw_scoreboard(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Create scoreboard
        scoreboard_width = 400
        scoreboard_height = 300
        scoreboard_x = (SCREEN_WIDTH - scoreboard_width) // 2
        scoreboard_y = (SCREEN_HEIGHT - scoreboard_height) // 2
        
        # Draw scoreboard background
        pygame.draw.rect(self.screen, (255, 255, 255), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height), 2)
        
        # Title
        font_title = pygame.font.SysFont('Arial', 28, bold=True)
        title = font_title.render("Game Over", True, (0, 0, 0))
        self.screen.blit(title, (scoreboard_x + (scoreboard_width - title.get_width()) // 2, 
                                 scoreboard_y + 20))
        
        # Sort players by score
        sorted_players = sorted(self.players, key=lambda player: player.score, reverse=True)
        
        # Find winner
        winner = sorted_players[0]
        
        # Display winner
        font_winner = pygame.font.SysFont('Arial', 24)
        winner_text = font_winner.render(f"Winner: {winner.name}", True, (0, 0, 0))
        self.screen.blit(winner_text, (scoreboard_x + (scoreboard_width - winner_text.get_width()) // 2, 
                                       scoreboard_y + 60))
        
        # Scores
        font_scores = pygame.font.SysFont('Arial', 20)
        for i, player in enumerate(sorted_players):
            text = font_scores.render(f"{player.name}: {player.score} points", True, (0, 0, 0))
            self.screen.blit(text, (scoreboard_x + 50, scoreboard_y + 100 + i * 30))
        
        # Restart instructions
        font_restart = pygame.font.SysFont('Arial', 16)
        restart_text = font_restart.render("Close and restart the game to play again", True, (0, 0, 0))
        self.screen.blit(restart_text, (scoreboard_x + (scoreboard_width - restart_text.get_width()) // 2, 
                                         scoreboard_y + scoreboard_height - 40))

if __name__ == "__main__":
    game = Game()
    game.run()