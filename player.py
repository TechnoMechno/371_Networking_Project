# TEST CODE player.py
from Plate import Plate
class Player:
    def __init__(self, player_id, address, plate_position, plate_radius, ):
        self.player_id = player_id            # Unique player ID
        self.address = address                # Tuple: (ip_address, port)
        self.name = f"Player {player_id}"
        self.score = 0
        self.mouse_pos = [0, 0]               # Current mouse position
        self.dragging_cookie = None           # Currently dragged cookie (if any)
        # Build the player's plate inside the Player object
        self.plate = Plate(plate_position, plate_radius)

    def to_dict(self):
        """
        Convert player information to a dictionary for sending to clients.
        """
        return {
            "player_id": self.player_id,
            "name": self.name,
            "score": self.score,
            "mouse_pos": self.mouse_pos,
            # Address info is usually kept server-side, but you can include it if needed.
            "address": self.address,
            "dragging_cookie": self.dragging_cookie
        }
    def gain_score(self, cookie):
    # Award points based on cookie type
        if cookie.type == "star":
            self.score += 2
        else:
            self.score += 1