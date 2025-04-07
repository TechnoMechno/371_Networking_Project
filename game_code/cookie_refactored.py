import pygame
import math
from game_code.config import REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, COOKIE_SIZE
import random

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
        #Releases the lock on the cookie if it is currently locked by the given player.
        if self.locked_by == player_id:
            self.locked_by = None
            return True
        return False

    def update_position(self, new_position):
        self.position = new_position
        
    def snap_to_player_plate(self, player):
        """
        Check if the cookie is within the player's plate boundaries.
        If yes, snap the cookie to the plate's center and return True.
        Otherwise, revert the cookie's position to its original position and return False.
        """
        # Extract player's plate position and radius.
        plate_pos = player.plate.position  # e.g., [x, y]
        plate_radius = player.plate.radius
        dx = self.position[0] - plate_pos[0]
        dy = self.position[1] - plate_pos[1]
        distance = math.hypot(dx, dy)
        if distance < plate_radius:
            # Get a random position so that cookie is not always in the centre.
            angle = random.uniform(0, 2 * math.pi)
            radius_offset = random.uniform(0, plate_radius - self.radius)

            offset_x = math.cos(angle) * radius_offset
            offset_y = math.sin(angle) * radius_offset

            # Snap the cookie to the plate's center.
            self.position = (plate_pos[0] + offset_x, plate_pos[1] + offset_y)
            self.on_plate = player.plate
            return True
        else:
            # Revert the cookie to its original position.
            self.position = self.original_position.copy()
            return False
    
    def is_on_central_plate(self, central_plate):
        """
        Checks if the cookie is on the central plate.
        """
        dx = self.position[0] - central_plate.x
        dy = self.position[1] - central_plate.y
        return math.hypot(dx, dy) < central_plate.radius
    
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