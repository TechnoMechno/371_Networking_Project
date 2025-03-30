import pygame
import math
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR
from cookie import Cookie
from player import Player
from ui import draw_cookies, draw_plate, draw_interface
from Plate import Plate

# Define game states
class GameState:
    BEFORE_START = 0
    PLAYING = 1
    GAME_OVER = 2

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cookie Dragging Prototype")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.BEFORE_START

        # Define UI buttons
        self.start_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25), (200, 50))
        self.restart_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100), (200, 50))
        
        # Initialize game objects
        self.setup_game_objects()
    
    def setup_game_objects(self):
        # Create the central plate
        self.central_plate = Plate(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 260)
        
        # Spawn 30 cookies on the central plate with more dispersed positions
        self.cookies = []
        num_cookies = 10
        spread_radius = 150  # Increased spread for more dispersion
        for i in range(num_cookies):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.x + r * math.cos(theta)
            y = self.central_plate.y + r * math.sin(theta)
            
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies.append(Cookie([x, y], cookie_type))
        
        # Setup players
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
            Plate(margin + plate_radius, margin + plate_radius, plate_radius),
            Plate(SCREEN_WIDTH - margin - plate_radius, margin + plate_radius, plate_radius),
            Plate(margin + plate_radius, SCREEN_HEIGHT - margin - plate_radius, plate_radius),
            Plate(SCREEN_WIDTH - margin - plate_radius, SCREEN_HEIGHT - margin - plate_radius, plate_radius)
        ]

    def restart_game(self):
        # Reinitialize game objects and set state to BEFORE_START
        self.setup_game_objects()
        self.state = GameState.BEFORE_START

    def start_game(self):
        self.state = GameState.PLAYING

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

            if self.state == GameState.BEFORE_START:
                # Check for Start button click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.start_game()
            elif self.state == GameState.PLAYING:
                # Pass event handling to cookies (in reverse so top cookie is prioritized)
                for cookie in reversed(self.cookies):
                    cookie.handle_event(event, self.player_plates, self.players)
            elif self.state == GameState.GAME_OVER:
                # Check for Restart button click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.restart_button_rect.collidepoint(event.pos):
                        self.restart_game()

    def update(self):
        if self.state == GameState.PLAYING:
            # Check if the game is over: e.g. no cookies left on the central plate
            cookies_on_central = any(
                abs(cookie.position[0] - self.central_plate.x) < self.central_plate.radius and 
                abs(cookie.position[1] - self.central_plate.y) < self.central_plate.radius 
                for cookie in self.cookies)
            cookies_on_player_plates = sum(
                1 for cookie in self.cookies if any(cookie.on_plate == plate for plate in self.player_plates))
            if not cookies_on_central and cookies_on_player_plates == len(self.cookies):
                self.state = GameState.GAME_OVER

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.central_plate.draw(self.screen)
        for plate in self.player_plates:
            plate.draw(self.screen)
        draw_cookies(self.screen, self.cookies)
        draw_interface(self.screen, self.players, self.player_plates)
        
        if self.state == GameState.BEFORE_START:
            # Draw Start button
            pygame.draw.rect(self.screen, (0, 255, 0), self.start_button_rect)
            font = pygame.font.SysFont('Arial', 24)
            text = font.render("Start Game", True, (0, 0, 0))
            self.screen.blit(text, (self.start_button_rect.x + (self.start_button_rect.width - text.get_width()) // 2,
                                      self.start_button_rect.y + (self.start_button_rect.height - text.get_height()) // 2))
        elif self.state == GameState.GAME_OVER:
            self.draw_scoreboard()
            # Draw Restart button
            pygame.draw.rect(self.screen, (0, 255, 0), self.restart_button_rect)
            font = pygame.font.SysFont('Arial', 24)
            text = font.render("Restart Game", True, (0, 0, 0))
            self.screen.blit(text, (self.restart_button_rect.x + (self.restart_button_rect.width - text.get_width()) // 2,
                                      self.restart_button_rect.y + (self.restart_button_rect.height - text.get_height()) // 2))
        
        pygame.display.flip()

    def draw_scoreboard(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        scoreboard_width = 400
        scoreboard_height = 300
        scoreboard_x = (SCREEN_WIDTH - scoreboard_width) // 2
        scoreboard_y = (SCREEN_HEIGHT - scoreboard_height) // 2
        
        pygame.draw.rect(self.screen, (255, 255, 255), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height), 2)
        
        font_title = pygame.font.SysFont('Arial', 28, bold=True)
        title = font_title.render("Game Over", True, (0, 0, 0))
        self.screen.blit(title, (scoreboard_x + (scoreboard_width - title.get_width()) // 2, 
                                  scoreboard_y + 20))
        
        sorted_players = sorted(self.players, key=lambda player: player.score, reverse=True)
        winner = sorted_players[0]
        
        font_winner = pygame.font.SysFont('Arial', 24)
        winner_text = font_winner.render(f"Winner: {winner.name}", True, (0, 0, 0))
        self.screen.blit(winner_text, (scoreboard_x + (scoreboard_width - winner_text.get_width()) // 2, 
                                        scoreboard_y + 60))
        
        font_scores = pygame.font.SysFont('Arial', 20)
        for i, player in enumerate(sorted_players):
            text = font_scores.render(f"{player.name}: {player.score} points", True, (0, 0, 0))
            self.screen.blit(text, (scoreboard_x + 50, scoreboard_y + 100 + i * 30))
        
        font_restart = pygame.font.SysFont('Arial', 16)
        restart_text = font_restart.render("Click Restart to play again", True, (0, 0, 0))
        self.screen.blit(restart_text, (scoreboard_x + (scoreboard_width - restart_text.get_width()) // 2, 
                                        scoreboard_y + scoreboard_height - 40))

if __name__ == "__main__":
    game = Game()
    game.run()