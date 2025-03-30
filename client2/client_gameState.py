"""
client_gameState.py - Maintains the local game state for the client.
This module holds a copy of the game state (cookies, players, assigned player id)
and provides methods to update that state based on messages received from the server.
"""

class ClientGameState:
    def __init__(self):
        self.cookies = {}   # e.g., {"0": {...}, "1": {...}, ...}
        self.players = {}   # e.g., {"1": {...}, "2": {...}, ...}
        self.assigned_player_id = None
    
    def handle_update(self, msg):
        msg_type = msg.get("type", "")
        if msg_type == "assign_id":
            self.assigned_player_id = msg.get("player_id")
            print("Assigned player id:", self.assigned_player_id)
        elif msg_type == "update_state":
            self.cookies = msg.get("cookies", {})
            self.players = msg.get("players", {})