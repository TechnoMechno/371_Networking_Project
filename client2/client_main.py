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

from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, COOKIE_SIZE, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE, GameState
from .client_networking import ClientNetworking
from .client_gameManager import ClientGameManager
from .render import load_assets, render
from .Button import Button
from .TextBox import TextBox

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
    game_manager = ClientGameManager()
    
    # Initialize networking and start receiving messages
    networking = ClientNetworking(SERVER_IP, SERVER_PORT)
    networking.add_receive_callback(lambda msg: game_manager.handle_update(msg))
    networking.start_receiving()

    dragging_cookie = None
    
    # Create UI elements. We'll create different ones based on game state.
    # For example, in MENU or LOBBY state, we want a "Start Game" button.
    start_button = Button((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 25, 200, 50), "Start Game", (0, 128, 0))
    # In GAME_OVER state, we want a "Reset Game" button.
    reset_button = Button((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 25, 200, 50), "Reset Game", (128, 0, 0))
    # Also, you might have a TextBox for entering a name in the MENU state.
    name_box = TextBox((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 40), "Enter Name")

    running = True
    while running:
        current_mouse_pos = list(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_manager.game_state == GameState.LOBBY.value:
                if start_button.handle_event(event):
                    # When Start Game is clicked, send a start_game message.
                    networking.send_message({"type": "start_game"})
                    print("Start game message sent")
            elif game_manager.game_state == GameState.GAME_OVER.value:
                if reset_button.handle_event(event):
                    networking.send_message({"type": "reset_game"})
                    print("Reset game message sent")
            elif game_manager.game_state == GameState.PLAYING.value:
                # HANDLE COOKIE DRAGGING IN PLAYING STATTE    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Use collision check to find which cookie is under the cursor
                    dragging_cookie = find_top_cookie(current_mouse_pos, game_manager.cookies)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_cookie = None

        # Send unified update message every frame.
        update_msg = {
            "type": "update",
            "position": current_mouse_pos,
            "dragged_cookie": dragging_cookie
        }

        networking.send_message(update_msg)

        if game_manager.game_state == GameState.LOBBY.value:
            start_button.draw(screen)
        elif game_manager.game_state == GameState.GAME_OVER.value:
            render(screen, game_manager, assets, game_manager.assigned_player_id)
            reset_button.draw(screen)
        elif game_manager.game_state == GameState.PLAYING.value:
            render(screen, game_manager, assets, game_manager.assigned_player_id)

        pygame.display.flip()
        clock.tick(60)
    
    networking.shutdown()
    pygame.quit()

if __name__ == "__main__":
    main()