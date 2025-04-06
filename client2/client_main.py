import pygame
import time
import json
import sys
import os
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, COOKIE_SIZE, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE, GameState
from .client_networking import ClientNetworking
from .client_gameManager import ClientGameManager
from .render import load_assets, render
from .Button import Button
from .TextBox import TextBox

#SERVER_IP = "142.58.214.104"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555

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

def draw_status_text(screen, status_message):
    """
    Renders a status message in brown at the center of the screen.
    """
    font = pygame.font.SysFont(None, 48)
    BROWN = (165, 42, 42)  # Brown color
    text_surface = font.render(status_message, True, BROWN)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text_surface, text_rect)

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
    
    # Create UI elements. Host (player 1) will see a button.
    start_button = Button((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 25, 200, 50), "Start Game", (101, 67, 33))
    back_button = Button((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 35, 200, 50), "Go Back", (101, 67, 33))
    reset_button = Button((SCREEN_WIDTH//2 - 65, SCREEN_HEIGHT//1.7, 120, 35), "Restart", (0, 0, 0))

    # Text boxes for names, IP Address of the host or whatever, and port numbers
    name_box = TextBox((SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 40), "Enter Name")
    ip_box = TextBox((SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 - 375, 275, 40), "Open IP Server: " + str(SERVER_IP))
    port_box = TextBox((SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 - 325, 275, 40), "Open Port: " + str(SERVER_PORT))


    running = True
    while running: 
        current_mouse_pos = list(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ✅ KEYDOWN event for pressing "R"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_manager.game_state == GameState.GAME_OVER.value:
                    if game_manager.assigned_player_id == 1:
                        networking.send_message({"type": "reset_game"})
                        print("[DEBUG] Sent reset_game")

            if game_manager.game_state == GameState.LOBBY.value:
                # Only allow host (player 1) to send the start_game command.
                if game_manager.assigned_player_id == 1:
                    if start_button.handle_event(event):
                        networking.send_message({"type": "start_game"})
                        print("Start game message sent")
                # Send a message to main to return to the main menu
                if back_button.handle_event(event):
                    print("Returning to Menu")
                    networking.shutdown() # Clean up the networking stuff before going back to main menu
                    return "Menu"
                    
            elif game_manager.game_state == GameState.GAME_OVER.value:
                # Only allow host to send reset_game command.
                if game_manager.assigned_player_id == 1:
                    if reset_button.handle_event(event):
                        networking.send_message({"type": "reset_game"})
                        print("Reset game message sent")
            elif game_manager.game_state == GameState.PLAYING.value:
                # Handle cookie dragging in PLAYING state.
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

        # Render game objects.
        render(screen, game_manager, assets, game_manager.assigned_player_id, reset_button)
        
        # Render UI based on game state and player role.
        if game_manager.game_state == GameState.LOBBY.value:
            if game_manager.assigned_player_id == 1:
                start_button.draw(screen)
                back_button.draw(screen)
                ip_box.draw(screen)
                port_box.draw(screen)
            else:
                back_button.draw(screen)
                draw_status_text(screen, "waiting for players")
                ip_box.draw(screen)
                port_box.draw(screen)
        # elif game_manager.game_state == GameState.GAME_OVER.value:
        #     if game_manager.assigned_player_id == 1:
        #         reset_button.draw(screen)
        #     else:
        #         draw_status_text(screen, "game ended - waiting for host")
        # In PLAYING state, no extra UI is needed; players see only the game.
        
        pygame.display.flip()
        clock.tick(60)
    
    networking.shutdown()
    pygame.quit()

if __name__ == "__main__":
    main()
