# cookie.py
import pygame
import math
from config import *

class Cookie:
          
    def __init__(self, cookie_id, position, type="regular"):
      self.cookie_id = cookie_id
      self.position = list(position)
      self.type = type
      try:
          image_path = REGULAR_COOKIE_IMAGE if self.type == "regular" else STAR_COOKIE_IMAGE
          self.image = pygame.image.load(image_path).convert_alpha()
          # Scale the image to COOKIE_SIZE
          self.image = pygame.transform.smoothscale(self.image, (COOKIE_SIZE, COOKIE_SIZE))
      except pygame.error as e:
          print(f"Error loading image: {e}")
          pygame.quit()
          exit()
      self.rect = self.image.get_rect(center=position)
      self.dragging = False
      self.locked_by = None  # No one is dragging this cookie initially
      self.offset = [0, 0]
      self.on_plate = None
      self.original_position = list(position)  # Save starting position
    def is_clicked(self, mouse_pos):
        """
        Returns True if mouse_pos is within this cookie's radius (circle check).
        """
        dx = mouse_pos[0] - self.position[0]
        dy = mouse_pos[1] - self.position[1]
        distance = math.hypot(dx, dy)
        return distance < self.radius

    def start_drag(self, player_id):
        """
        Attempt to lock the cookie for dragging.
        
        Parameters:
          player_id (int): The ID of the player who wants to drag the cookie.
          
        Returns:
          bool: True if the cookie was successfully locked; False otherwise.
        """
        if self.locked_by is None:
            self.locked_by = player_id
            return True
        return False

    def stop_drag(self, player_id):
        """
        Unlock the cookie, if it is currently locked by the given player.
        
        Parameters:
          player_id (int): The ID of the player releasing the cookie.
          
        Returns:
          bool: True if the cookie was unlocked; False otherwise.
        """
        if self.locked_by == player_id:
            self.locked_by = None
            return True
        return False

    def update_position(self, new_position):
        """
        Update the cookie's position.
        
        Parameters:
          new_position (list): The new [x, y] coordinates.
        """
        self.position = new_position

    def to_dict(self):
        """
        Convert the cookie's state to a dictionary for serialization.
        
        Returns:
          dict: Dictionary representation of the cookie.
        """
        return {
            "cookie_id": self.cookie_id,
            "position": self.position,
            "cookie_type": self.cookie_type,
            "locked_by": self.locked_by
        }

    def __str__(self):
        return f"Cookie({self.cookie_id}, pos={self.position}, type={self.cookie_type}, locked_by={self.locked_by})"


# Example usage:
if __name__ == "__main__":
    # Create a regular cookie with ID 1 at position [100, 150]
    cookie = Cookie(cookie_id=1, position=[100, 150])
    print(cookie)

    # Simulate player 2 starting to drag the cookie
    if cookie.start_drag(player_id=2):
        print("Cookie locked by player 2.")
    else:
        print("Failed to lock cookie.")
    print(cookie)

    # Update the cookie position as player 2 drags it
    cookie.update_position([120, 170])
    print("After dragging:", cookie)

    # Player 2 releases the cookie
    if cookie.stop_drag(player_id=2):
        print("Cookie released by player 2.")
    else:
        print("Failed to release cookie.")
    print(cookie)

    # Convert cookie to dict for JSON serialization
    print("Cookie state as dict:", cookie.to_dict())