import pygame
import time
import json
import sys
import os

"""
client_main.py - Entry point for the Cookie Dragging Game Client.
This file initializes Pygame, loads assets, sets up the game state and networking,
and runs the main game loop which handles input and rendering.
"""

# Add parent directory to sys.path so that game_code can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, COOKIE_SIZE, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE
from client_networking import ClientNetworking
from client2.client_gameManager import ClientGameManager
from render import load_assets, render

#SERVER_IP = "142.58.214.104"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

def find_top_cookie(mouse_pos, cookies):
    """
    Given the current mouse position and the cookies dictionary (from server state),
    returns the ID of the topmost cookie under the cursor.
    Assumes cookies with higher numeric IDs (converted from keys) are drawn on top.
    """
    # Convert keys to integers, sort in descending order.
    for cid in sorted([int(k) for k in cookies.keys()], reverse=True):
        cookie = cookies[str(cid)]  # assuming keys in the dict are strings
        pos = cookie.get("position", [0, 0])
        radius = cookie.get("radius", 30)
        dx = mouse_pos[0] - pos[0]
        dy = mouse_pos[1] - pos[1]
        if (dx * dx + dy * dy) ** 0.5 < radius:
            return str(cid)
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cookie Dragging Game Client")
    clock = pygame.time.Clock()

    # Load image assets AFTER display is initialized
    assets = load_assets()  # load_assets() taken from 'render.py'

    # Initialize game state
    game_state = ClientGameManager()
    
    # Initialize networking and start receiving messages
    networking = ClientNetworking(SERVER_IP, SERVER_PORT)
    networking.add_receive_callback(lambda msg: game_state.handle_update(msg))
    networking.start_receiving()

    dragging_cookie = None

    running = True
    while running:
        current_mouse_pos = list(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Use collision check to find which cookie is under the cursor
                dragging_cookie = find_top_cookie(current_mouse_pos, game_state.cookies)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_cookie = None

        # Send unified update message every frame.
        update_msg = {
            "type": "update",
            "position": current_mouse_pos,
            "dragged_cookie": dragging_cookie
        }
        print("Sending update:", current_mouse_pos, dragging_cookie)

        networking.send_message(update_msg)

        # Render the current game state
        render(screen, game_state, assets, game_state.assigned_player_id)
        clock.tick(60)
    
    networking.shutdown()
    pygame.quit()

if __name__ == "__main__":
    main()