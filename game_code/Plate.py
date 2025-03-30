import pygame
import os
from game_code.config import PLATE_IMAGE

class Plate:
    def __init__(self, position, radius):
        self.position = position  # [x, y]
        self.radius = radius      # The plate's size

    def to_dict(self):
        return {"position": self.position, "radius": self.radius}