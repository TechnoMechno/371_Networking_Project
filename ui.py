# ui.py
import pygame
from config import *

def draw_cookies(screen, cookies):
    for cookie in cookies:
        cookie.draw(screen)  # Call each cookie’s draw method

def draw_plate(screen):
    pygame.draw.rect(screen, (169, 169, 169), (350, 550, 100, 10))  # Simple gray plate

# Placeholder for score display
def draw_interface(screen, players, player_plates):
    # Display player information near their plates
    font = pygame.font.SysFont('Arial', 18)
    
    for i, (player, plate) in enumerate(zip(players, player_plates)):
        text = font.render(f"{player.name}: {player.score}", True, (0, 0, 0))
        
        # Position the text above or below the plate based on its position
        if i < 2:  # Top plates (above)
            text_pos = (plate.x - text.get_width() // 2, plate.y - plate.radius - 30)
        else:  # Bottom plates (below)
            text_pos = (plate.x - text.get_width() // 2, plate.y + plate.radius + 10)
            
        screen.blit(text, text_pos)