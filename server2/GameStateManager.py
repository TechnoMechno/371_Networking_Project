# GameStateManager.py
import threading
import json
import math
import random
from game_code.player import Player
from game_code.cookie_refactored import Cookie
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, COOKIE_COUNT, GameState
from game_code.Plate import Plate

# -------------------------------------------------------------
# This module maintains the authoritative game state on the server.
# It manages players, cookies, and client addresses, processes incoming
# JSON messages from clients, and provides the full game state as a dictionary
# for broadcasting to connected clients.
# -------------------------------------------------------------

class GameStateManager:
    def __init__(self):
        # Dictionaries to hold game objects
        self.players = {}           # Format: {player_id: Player}
        self.cookies = {}           # Format: {cookie_id: Cookie}
        self.client_addresses = {}  # Format: {addr: player_id}
        self.game_state = GameState.LOBBY
        
        self.next_player_id = 1     # Incrementing player id
        self.lock = threading.Lock()  # For thread safety
        
        # Create the central plate (for example, centered in the screen)
        central_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        central_plate_radius = 260  # or any value you choose
        self.central_plate = Plate(central_position, central_plate_radius)

        # Randomly spawn cookies
        spread_radius = 150  # Increased spread for more dispersion
        for i in range(COOKIE_COUNT):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.position[0] + r * math.cos(theta)
            y = self.central_plate.position[1] + r * math.sin(theta)
            
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies[i] = Cookie(cookie_id=i, position=[x, y])

    def handle_message(self, message, addr, udp_socket):
        """
        Processes a JSON message from a client.
        - If addr is new, register a new Player.
        - Otherwise, update state based on the unified 'update' message.
        """
        try:
            data_obj = json.loads(message)
        except Exception as e:
            print("JSON error in handle_message:", e)
            return
        
        with self.lock:
            # Register new client if not present
            if addr not in self.client_addresses:
                if self.next_player_id <= 4:  # Limit to 4 players
                    player_id = self.next_player_id
                    self.next_player_id += 1
                    self.client_addresses[addr] = player_id
                    # Calculate plate position based on screen dimensions
                    plate_position = self.calculate_plate_position(player_id, SCREEN_WIDTH, SCREEN_HEIGHT)
                    # Make sure the Player class initializes a score attribute, e.g. self.score = 0
                    self.players[player_id] = Player(player_id, addr, plate_position, plate_radius=150)
                    # Send assign_id message to client
                    assign_msg = {"type": "assign_id", "player_id": player_id}
                    udp_socket.sendto(json.dumps(assign_msg).encode(), addr)
                    print(f"Registered new player {player_id} from {addr}")
                else:
                    # Server full, optionally send a "server_full" message.
                    udp_socket.sendto(json.dumps({"type": "server_full"}).encode(), addr)
                    return

            # Process a unified update message from a client.
            if data_obj.get("type") == "update":
                player_id = self.client_addresses[addr]
                # Update the player's mouse position
                self.players[player_id].mouse_pos = data_obj.get("position", self.players[player_id].mouse_pos)
                dragged = data_obj.get("dragged_cookie")
                
                # Process dragging: 'dragged_cookie' might be null or a cookie id
                if dragged is None:
                    # Release any cookie locked by this player.
                    for cookie in self.cookies.values():
                        if cookie.locked_by == player_id:
                            snapped = cookie.snap_to_player_plate(self.players[player_id])
                            if snapped:
                                self.players[player_id].score += 1
                            else:
                                # If not snapped, revert to original position.
                                cookie.update_position(cookie.original_position)
                            cookie.locked_by = None
                else:
                    # The client is dragging a cookie.
                    dragged = int(dragged)
                    cookie = self.cookies.get(dragged)
                    
                    if cookie:
                        # Check if the mouse is over the cookie.
                        if cookie.is_clicked(self.players[player_id].mouse_pos):
                            # Lock the cookie to this player and update its position.
                            if cookie.locked_by is None or cookie.locked_by == player_id:
                                cookie.locked_by = player_id
                                cookie.update_position(self.players[player_id].mouse_pos)
            elif data_obj.get("type") == "start_game":
                # Only allow player 1 to start the game (!!!!currently commented out)
                player_id = self.client_addresses[addr]
                # if player_id == 1:
                self.start_game_flag = True
                print("Received start_game command from host.")
            elif data_obj.get("type") == "reset_game":
                player_id = self.client_addresses[addr]
                if player_id == 1:
                    self.reset_game_flag = True
                    # Reset all players' scores and cookies
                    print("Received reset_game command.")
                                
    def update_dragged_cookies(self):
        with self.lock:
            for cookie in self.cookies.values():
                if cookie.locked_by is not None and cookie.locked_by in self.players:
                    cookie.update_position(self.players[cookie.locked_by].mouse_pos)

    def get_scoreboard_data(self):
        scoreboard_positions = [
            {"x": 10, "y": 10},               # Top left
            {"x": SCREEN_WIDTH - 200, "y": 10}, # Top right
            {"x": 10, "y": SCREEN_HEIGHT - 50}, # Bottom left
            {"x": SCREEN_WIDTH - 200, "y": SCREEN_HEIGHT - 50}  # Bottom right
        ]
        scoreboard = {}
        sorted_players = sorted(self.players.items(), key=lambda x: x[0])
        for index, (player_id, player) in enumerate(sorted_players):
            scoreboard[str(player_id)] = {
                "player": f"Player {player_id}",
                "score": getattr(player, 'score', 0),
                "position": scoreboard_positions[index]
            }
        return scoreboard


    def get_game_data(self):
        """
        Returns the full game state as a dictionary for broadcasting.
        This now includes a 'scoreboard' entry with each player's score and its designated corner position.
        """
        with self.lock:
            state = {
                "type": "update_state",
                "game_state": self.game_state.value,
                "central_plate": self.central_plate.to_dict(),
                "cookies": {str(cid): cookie.to_dict() for cid, cookie in self.cookies.items()},
                "players": {str(pid): player.to_dict() for pid, player in self.players.items()},
                "scoreboard": self.get_scoreboard_data() 
            }
        return state

    def get_all_client_addresses(self):
        """
        Returns a list of all client addresses.
        """
        with self.lock:
            return list(self.client_addresses.keys())

    def update_state_transitions(self):
        # Transition from LOBBY to PLAYING:
        if self.game_state == GameState.LOBBY:
            if getattr(self, 'start_game_flag', False) and len(self.players) >= 1:
                self.game_state = GameState.PLAYING
                print("Transition: LOBBY -> PLAYING")
                self.start_game_flag = False
        
        # Transition from PLAYING to GAME_OVER:
        elif self.game_state == GameState.PLAYING:
            all_collected = all(cookie.on_plate is not None for cookie in self.cookies.values())
            if all_collected:
                self.game_state = GameState.GAME_OVER
                print("Transition: PLAYING -> GAME_OVER")
        
        # Transition from GAME_OVER back to LOBBY:
        elif self.game_state == GameState.GAME_OVER:
            if getattr(self, 'reset_game_flag', False):
                self.reset_game()
    
    def reset_game(self):
        # Reset player scores.
        for player in self.players.values():
            player.score = 0

        # Reinitialize cookies.
        self.cookies = {}
        spread_radius = 150  # Use the same spread value as before.
        for i in range(COOKIE_COUNT):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.position[0] + r * math.cos(theta)
            y = self.central_plate.position[1] + r * math.sin(theta)
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies[i] = Cookie(cookie_id=i, position=[x, y])
    
        # Optionally, if your Cookie class has additional state (e.g., locked_by, on_plate),
        # the new Cookie objects will start in their default state.
    
        # Reset the game state to LOBBY and clear the reset flag.
        self.game_state = GameState.LOBBY
        self.reset_game_flag = False
        print("Transition: GAME_OVER -> LOBBY")

    @staticmethod
    def calculate_plate_position(player_index, screen_width, screen_height, margin=30, plate_radius=150):
        # For players 1 and 3, x is on the left; for 2 and 4, on the right.
        x = margin + plate_radius if player_index % 2 == 1 else screen_width - margin - plate_radius
        # For players 1 and 2, y is on the top; for 3 and 4, on the bottom.
        y = margin + plate_radius if player_index <= 2 else screen_height - margin - plate_radius
        return [x, y]
