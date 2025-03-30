import pygame
import math
from game_code.config import REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, COOKIE_SIZE

class Cookie:
    def __init__(self, cookie_id, position, type="regular"):
        self.cookie_id = cookie_id
        self.position = list(position)
        self.type = type
        self.locked_by = None  # No one is dragging this cookie initially
        self.offset = [0, 0]
        self.on_plate = None
        self.original_position = list(position)
        self.radius = 30

    def is_clicked(self, mouse_pos):
        dx = mouse_pos[0] - self.position[0]
        dy = mouse_pos[1] - self.position[1]
        distance = math.hypot(dx, dy)
        return distance < self.radius

    def start_drag(self, player_id):
        if self.locked_by is None:
            self.locked_by = player_id
            return True
        return False

    def stop_drag(self, player_id):
        if self.locked_by == player_id:
            self.locked_by = None
            return True
        return False

    def update_position(self, new_position):
        self.position = new_position

    def to_dict(self):
        return {
            "cookie_id": self.cookie_id,
            "position": self.position,
            "cookie_type": self.type,
            "locked_by": self.locked_by,
            "radius": self.radius
        }

    def __str__(self):
        return f"Cookie({self.cookie_id}, pos={self.position}, type={self.type}, locked_by={self.locked_by})"