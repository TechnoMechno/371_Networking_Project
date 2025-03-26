# from config import *
# import pygame
# import random

# class Plate:
#     def __init__(self, x, y, radius, image_file="Assets/plate.png"):
#         self.x = x
#         self.y = y
#         self.radius = radius
#         # Load and scale the plate image
#         self.image = pygame.image.load(image_file).convert_alpha()
#         self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
#         self.rect = self.image.get_rect(center=(x, y))
        
#     def draw(self, screen):
#         screen.blit(self.image, self.rect)


# plate.py
class Plate:
    def __init__(self, position, radius):
        self.position = position  # e.g., [x, y]
        self.radius = radius      # The plate's size

    def to_dict(self):
        return {"position": self.position, "radius": self.radius}