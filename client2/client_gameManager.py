"""
client_gameState.py - Maintains the local game state for the client.
This module holds a copy of the game state (cookies, players, assigned player id)
and provides methods to update that state based on messages received from the server.
"""
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, GameState
from game_code.Plate import Plate


class ClientGameManager:
    #Initializes Game state for cookies, players, object positions, and game state.
    def __init__(self):
        self.cookies = {}   # e.g., {"0": {...}, "1": {...}, ...}
        self.players = {}   # e.g., {"1": {...}, "2": {...}, ...}
        self.assigned_player_id = None
        # Create the central plate (for example, centered in the screen)
        central_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        central_plate_radius = 260  # or any value you choose
        self.central_plate = Plate(central_position, central_plate_radius)
        self.game_state = GameState.LOBBY
        self.start_game_flag = False
        self.reset_game_flag = False
    
    #Handles updates for the state of the game, like cookies, players, and scores
    def handle_update(self, msg):
        msg_type = msg.get("type", "")
        if msg_type == "assign_id":
            self.assigned_player_id = msg.get("player_id")
            print("Assigned player id:", self.assigned_player_id)
        elif msg_type == "update_state":
            self.cookies = msg.get("cookies", {})
            self.players = msg.get("players", {})
            self.game_state = msg.get("game_state")
            self.scoreboard = msg.get("scoreboard", {})
        elif msg_type == "shutdown":
            self.server_shutdown = True
            
