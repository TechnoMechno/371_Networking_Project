from cookie import Cookie
import socket 
import threading
import pygame
import json
from shared import GameState, game_state 

# PORT and IP Address
PORT = 5555 w
ip_address = "localhost"

in_game = Falseww
player_id = -1 # The player ID assigned by the server.
cookie_id = -1 # The cookie ID picked up by player
mouse_x = pygame.mouse.get_pos()[0]
mouse_y = pygame.mouse.get_pos()[1]
is_dragging = False

client_cookies = {}

update_message = {
    'player_id': player_id,
    'mouse_x': mouse_x,
    'mouse_y': mouse_y,
    'cookie_id': cookie_id,
    'is_dragging': is_dragging
}

class GameClient:
    def __init__(self, player_id):
        self.player_id = player_id

    def join_game(self):
        """Join the game lobby."""
        # TODO: implement client to server 
        pass

    def receive_from_server(client_socket):
        """Receive messages from the server."""
        while True:
            data = client_socket.recv(1024)
            try:
                data = client_socket.recv(4096).decode()
                if not data:
                    continue
                data_obj = json.loads(data)
                if data_obj['type'] == 'update':
                    server_cookies = data_obj['cookies']
                    for cookie_id, cookie_data in server_cookies.items():
                        cookie_id = int(cookie_id)

                        if (cookie_id) in client_cookies:
                            client_cookies[cookie_id].position = cookie_data["position"]
                            client_cookies[cookie_id].cookie_type = cookie_data["cookie_type"]
                            client_cookies[cookie_id].locked_by = cookie_data["locked_by"]
                elif data_obj['type'] == "update_state":
                    pass 
                else:
                    player_id = data_obj['player_id']
                    pass
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def if_dragging(self):
        """Check if the player is dragging the cookie."""
        global is_dragging 
        if (pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pos() == (cookie)):
            is_dragging = True
        else:
            is_dragging = False
        pass

    def get_mouse_location():
        """Get coordinates from website."""
        global mouse_x, mouse_y
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]

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

    def tick():
        """Update the game state."""
        pass
        
def main():
    server_address = (ip_address, PORT) 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.connect(server_address)




