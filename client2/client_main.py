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

#SERVER_IP = "142.58.214.104"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555

def find_top_cookie(mouse_pos, cookies):
    """
    Given the current mouse position and the cookies dictionary,
    returns the ID of the topmost cookie under the cursor.
    Assumes cookies with higher numeric IDs (converted from keys) are drawn on top.
    """
    for cid in sorted([int(k) for k in cookies.keys()], reverse=True):
        cookie = cookies[str(cid)]
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
    BROWN = (165, 42, 42)
    text_surface = font.render(status_message, True, BROWN)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def main(server_ip, server_port):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cookie Dragging Game Client")
    clock = pygame.time.Clock()

    # Load assets (make sure your render.py is set up accordingly)
    assets = load_assets()

    # Initialize game state and networking
    game_manager = ClientGameManager()
    networking = ClientNetworking(server_ip, server_port)
    networking.add_receive_callback(lambda msg: game_manager.handle_update(msg))
    networking.start_receiving()

    dragging_cookie = None

    # UI elements:
    # - start_button and reset_button for host actions
    # - back_button to return to the main menu
    start_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50), "Start Game", (0, 128, 0))
    reset_button = Button((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50), "Reset Game", (128, 0, 0))
    back_button = Button((10, 10, 120, 40), "Menu", (200, 0, 0))

    running = True
    while running:
        current_mouse_pos = list(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # Returning False here can signal a full exit (if you prefer)
                return False

            # Check if "Back to Menu" is pressed:
            if back_button.handle_event(event):
                # Exit game loop and return to main menu
                running = False
                return True

            if game_manager.game_state == GameState.LOBBY.value:
                # Only host (player 1) can send the start_game command.
                if game_manager.assigned_player_id == 1:
                    if start_button.handle_event(event):
                        networking.send_message({"type": "start_game"})
                        print("Start game message sent")
            elif game_manager.game_state == GameState.GAME_OVER.value:
                # Only host can send reset_game command.
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
        render(screen, game_manager, assets, game_manager.assigned_player_id)
        if game_manager.game_state == GameState.LOBBY.value:
            if game_manager.assigned_player_id == 1:
                start_button.draw(screen)
            else:
                draw_status_text(screen, "waiting for players")
        elif game_manager.game_state == GameState.GAME_OVER.value:
            if game_manager.assigned_player_id == 1:
                reset_button.draw(screen)
            else:
                draw_status_text(screen, "game ended - waiting for host")
        
        # Always draw the back-to-menu button.
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    networking.shutdown()
    pygame.quit()
    return True


if __name__ == "__main__":
    main()
