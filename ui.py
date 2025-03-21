# ui.py
import pygame
from config import *

def draw_cookies(screen, cookies):
    for cookie in cookies:
        cookie.draw(screen)  # Call each cookie’s draw method

def draw_plate(screen):
    pygame.draw.rect(screen, (169, 169, 169), (350, 550, 100, 10))  # Simple gray plate

# Placeholder for score display
def draw_interface(screen, players):
    pass  # To be implemented later