# TEST CODE player.py
from game_code.Plate import Plate

PLAYER_COLORS = [
    (255, 0, 0),   # Red for Player 1
    (0, 255, 0),   # Green for Player 2
    (0, 0, 255),   # Blue for Player 3
    (255, 165, 0)  # Yellow for Player 4
]

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
        self.color = PLAYER_COLORS[(player_id - 1) % len(PLAYER_COLORS)]

    def to_dict(self):
        """
        Convert player information to a dictionary for sending to clients.
        """
        data = {
            "player_id": self.player_id,
            "name": self.name,
            "score": self.score,
            "mouse_pos": self.mouse_pos,
            "dragging_cookie": self.dragging_cookie,
            # Don't include 'address' unless you really need it
            # "address": self.address,
            "color": self.color  # Color as an RGB tuple, e.g., [255, 0, 0]
        }

        # Include plate only if it exists
        if self.plate:
            data["plate"] = {
                "plate_position": self.plate.position,
                "plate_radius": self.plate.radius
            }

        return data
        
    def gain_score(self, cookie):
    # Award points based on cookie type
        if cookie.type == "star":
            self.score += 2
        else:
            self.score += 1