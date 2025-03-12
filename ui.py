# ui.py
import pygame
from config import *

def draw_pancakes(screen, pancakes):
    for pancake in pancakes:
        pancake.draw(screen)  # Call each pancake’s draw method

def draw_plate(screen):
    pygame.draw.rect(screen, (169, 169, 169), (350, 550, 100, 10))  # Simple gray plate

# Placeholder for score display
def draw_scores(screen, players):
    pass  # To be implemented later