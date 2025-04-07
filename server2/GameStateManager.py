import threading
import json
import math
import random
from game_code.player import Player
from game_code.cookie_refactored import Cookie
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, COOKIE_COUNT, GameState
from game_code.Plate import Plate

class GameStateManager:
    # For convenience, define a class-level constant for the lobby state.
    LOBBY = GameState.LOBBY

    def __init__(self):
        # Dictionaries to hold game objects.
        self.players = {}           # Format: {player_id: Player}
        self.cookies = {}           # Format: {cookie_id: Cookie}
        self.client_addresses = {}  # Format: {addr: player_id}
        self.game_state = GameState.LOBBY
        
        self.next_player_id = 1     # Incrementing player id
        self.lock = threading.RLock()  # For thread safety
        
        # Create the central plate (centered on the screen).
        central_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        central_plate_radius = 260  # You can adjust this value.
        self.central_plate = Plate(central_position, central_plate_radius)

        # Spawn cookies randomly.
        spread_radius = 150  # Spread radius for cookie placement.
        for i in range(COOKIE_COUNT):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.position[0] + r * math.cos(theta)
            y = self.central_plate.position[1] + r * math.sin(theta)
            
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies[i] = Cookie(cookie_id=i, position=[x, y], type=cookie_type)

    def handle_message(self, message, addr, udp_socket):
        """
        Processes a JSON message from a client.
        Registers new players if necessary, or processes updates.
        """
        try:
            data_obj = json.loads(message)
        except Exception as e:
            print("JSON error in handle_message:", e)
            return
        
        with self.lock:
            # Register new client if not present.
            if addr not in self.client_addresses:
                # If game is in session, notify the client that it cannot join.
                if self.game_state != GameState.LOBBY:
                    alert_msg = {"type": "game_in_session"}
                    udp_socket.sendto(json.dumps(alert_msg).encode(), addr)
                    return 
                
                # Allow up to 4 players by finding a free id.
                available_id = None
                for i in range(1, 5):
                    if i not in self.players:
                        available_id = i
                        break
                if available_id is None:
                    udp_socket.sendto(json.dumps({"type": "server_full"}).encode(), addr)
                    return

                player_id = available_id
                self.client_addresses[addr] = player_id
                plate_position = self.calculate_plate_position(player_id, SCREEN_WIDTH, SCREEN_HEIGHT)
                self.players[player_id] = Player(player_id, addr, plate_position, plate_radius=150)
                assign_msg = {"type": "assign_id", "player_id": player_id}
                udp_socket.sendto(json.dumps(assign_msg).encode(), addr)
                print(f"Registered new player {player_id} from {addr}")

            # Process update messages.
            if data_obj.get("type") == "update":
                player_id = self.client_addresses[addr]
                self.players[player_id].mouse_pos = data_obj.get("position", self.players[player_id].mouse_pos)
                dragged = data_obj.get("dragged_cookie")
                
                if dragged is None:
                    for cookie in self.cookies.values():
                        if cookie.locked_by == player_id:
                            snapped = cookie.snap_to_player_plate(self.players[player_id])
                            if snapped:
                                if cookie.type == 'star':
                                    self.players[player_id].score += 2
                                else:
                                    self.players[player_id].score += 1
                            else:
                                cookie.update_position(cookie.original_position)
                            cookie.locked_by = None
                else:
                    dragged = int(dragged)
                    cookie = self.cookies.get(dragged)
                    if cookie:
                        if cookie.on_plate is None:
                            if cookie.is_clicked(self.players[player_id].mouse_pos):
                                if cookie.locked_by is None or cookie.locked_by == player_id:
                                    cookie.locked_by = player_id
                                    cookie.update_position(self.players[player_id].mouse_pos)
                        else:
                            pass
            elif data_obj.get("type") == "start_game":
                player_id = self.client_addresses[addr]
                self.start_game_flag = True
                print("Received start_game command from host.")
            elif data_obj.get("type") == "reset_game":
                player_id = self.client_addresses[addr]
                if player_id == 1:
                    self.reset_game_flag = True
                    print("Received reset_game command.")
                else:
                    print(f"Player {player_id} attempted to reset the game but is not authorized.")
            elif data_obj.get("type") == "quit":
                print("a player quit!")
                self.handle_player_disconnect(addr)
                return
                                
    def update_dragged_cookies(self):
        with self.lock:
            for cookie in self.cookies.values():
                if cookie.locked_by is not None and cookie.locked_by in self.players:
                    cookie.update_position(self.players[cookie.locked_by].mouse_pos)

    def get_scoreboard_data(self):
        scoreboard_positions = [
            {"x": 10, "y": 10},
            {"x": SCREEN_WIDTH - 200, "y": 10},
            {"x": 10, "y": SCREEN_HEIGHT - 50},
            {"x": SCREEN_WIDTH - 200, "y": SCREEN_HEIGHT - 50}
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
        # print(json.dumps(state, indent=2))

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
        with self.lock:
            return list(self.client_addresses.keys())

    def update_state_transitions(self):
        if self.game_state == GameState.LOBBY:
            if getattr(self, 'start_game_flag', False) and len(self.players) >= 1:
                self.game_state = GameState.PLAYING
                print("Transition: LOBBY -> PLAYING")
                self.start_game_flag = False
        elif self.game_state == GameState.PLAYING:
            all_collected = all(cookie.on_plate is not None for cookie in self.cookies.values())
            if all_collected:
                self.game_state = GameState.GAME_OVER
                print("Transition: PLAYING -> GAME_OVER")
        elif self.game_state == GameState.GAME_OVER:
            if getattr(self, 'reset_game_flag', False):
                self.reset_game()
    
    def reset_game(self):
        for player in self.players.values():
            player.score = 0
        self.cookies = {}
        spread_radius = 150
        for i in range(COOKIE_COUNT):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.position[0] + r * math.cos(theta)
            y = self.central_plate.position[1] + r * math.sin(theta)
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies[i] = Cookie(cookie_id=i, position=[x, y], type=cookie_type)
        self.game_state = GameState.LOBBY
        self.reset_game_flag = False
        print("Transition: GAME_OVER -> LOBBY")

    def handle_player_disconnect(self, addr):
        with self.lock:
            if addr in self.client_addresses:
                player_id = self.client_addresses.pop(addr)
                
                # Identify player's plate object (if it exists)
                player_plate = None
                if player_id in self.players:
                    player_plate = self.players[player_id].plate
                

                # Revert any cookies on that player's plate to their initial position.
                if player_plate:
                    for cookie in self.cookies.values():
                        if cookie.on_plate == player_plate:
                            cookie.on_plate = None
                            cookie.update_position(cookie.original_position)
                        
                if player_id in self.players:
                    del self.players[player_id]
                print(f"Player {player_id} disconnected.")
                
                # Recalculate next_player_id to be the smallest missing number in [1, 4].
                used_ids = set(self.players.keys())
                for i in range(1,5):
                    if i not  in used_ids:
                        self.next_player_id = i
                        break
    @staticmethod
    def calculate_plate_position(player_index, screen_width, screen_height, margin=30, plate_radius=150):
        x = margin + plate_radius if player_index % 2 == 1 else screen_width - margin - plate_radius
        y = margin + plate_radius if player_index <= 2 else screen_height - margin - plate_radius
        return [x, y]
