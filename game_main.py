import pygame
import sys
import socket
import json
import threading
import ipaddress
import time

# Import configuration and supporting modules.
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, CREAM, BROWN, WHITE, BLACK, GameState
from client2.render import load_assets, render
from client2.client_networking import ClientNetworking
from client2.client_gameManager import ClientGameManager
from client2.Button import Button
from client2.TextBox import TextBox
from server2 import server_main


# Define dimensions for menu and game screens.
MENU_WIDTH, MENU_HEIGHT = 600, 400
GAME_WIDTH, GAME_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT

# handshake function for udp
def is_server_listening(ip_address, port):
    """
    Send a UDP 'JOIN_CHECK' message to the server and expect:
      - "PONG" as a plain text response if join is allowed, or
      - A JSON message with type "game_in_session" if the game is busy.
    """
    test_message = "JOIN_CHECK"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)  # 1-second timeout for response
    try:
        sock.sendto(test_message.encode(), (ip_address, port))
        data, addr = sock.recvfrom(1024)
        response_str = data.decode().strip()
        try:
            response_obj = json.loads(response_str)
            if response_obj.get("type") == "game_in_session":
                return False, response_obj.get("message", "Game is already in session. Cannot join.")
        except json.JSONDecodeError:
            if response_str == "PONG":
                return True, None
            else:
                return False, "Unexpected handshake response: " + response_str
    except socket.timeout:
        return False, f"No server running on IP: {ip_address} and port: {port}"
    except Exception as e:
        return False, "Handshake error: " + str(e)
    finally:
        sock.close()

##############################################
# MAIN MENU (IN CLIENT)
##############################################
def run_main_menu(screen, default_host=False):
    mode_selection = None

    # Create two buttons for starting or joining a game.
    start_button = Button(rect=(200, 200, 200, 60), text="Start a Game", bg_color=BROWN,
                          text_color=WHITE, font_size=30, callback=lambda: set_mode("start"))
    join_button = Button(rect=(200, 280, 200, 60), text="Join a Game", bg_color=BROWN,
                         text_color=WHITE, font_size=30, callback=lambda: set_mode("join"))
    buttons = [start_button, join_button]
    
    title_font = pygame.font.SysFont("comicsansms", 64)
    
    # Attempt to load a background cookie image.
    try:
        cookie_img = pygame.image.load("Assets/cookie.png").convert_alpha()
        cookie_img = pygame.transform.scale(cookie_img, (64, 64))
    except pygame.error:
        cookie_img = None
    cookie_positions = []
    if cookie_img:
        cookie_positions = [
            (30, 30),
            (MENU_WIDTH - 50 - 64, 30),
            (30, MENU_HEIGHT - 30 - 64),
            (MENU_WIDTH - 30 - 64, MENU_HEIGHT - 30 - 64),
            (MENU_WIDTH // 2 - 32, MENU_HEIGHT // 2 - 50),
            (10, MENU_HEIGHT // 2 - 40),
            (MENU_WIDTH - 150, MENU_HEIGHT // 2 - 24)
        ]
    
    def set_mode(selection):
        nonlocal mode_selection
        mode_selection = selection

    clock = pygame.time.Clock()
    while mode_selection is None:
        screen.fill(CREAM)
        if cookie_img:
            for pos in cookie_positions:
                screen.blit(cookie_img, pos)
        title_surface = title_font.render("COOKIE GRABBER", True, BROWN)
        title_rect = title_surface.get_rect(center=(MENU_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for btn in buttons:
                btn.handle_event(event)
        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    # If the user chose to join, prompt for IP/port.
    if mode_selection == "join":
        result = ip_input_screen(screen, auto_start=not default_host)
        if result is None:
            return run_main_menu(screen)  # Restart menu if join cancelled.
        else:
            server_ip, server_port = result
    else:
        # For "start", assume hosting on localhost.
        server_ip, server_port = "127.0.0.1", 55555
    return mode_selection, server_ip, server_port, mode_selection == "start"



# input screen to join
def ip_input_screen(screen, auto_start=True):
    clock = pygame.time.Clock()
    error_message = None
    ip_box = TextBox(rect=(MENU_WIDTH // 2 - 150, 160, 300, 40), text="Enter IP",
                     font_size=30, bg_color=WHITE, text_color=BLACK,
                     border_color=BROWN, border_width=2)
    port_box = TextBox(rect=(MENU_WIDTH // 2 - 150, 220, 300, 40), text="Enter Port",
                       font_size=30, bg_color=WHITE, text_color=BLACK,
                       border_color=BROWN, border_width=2)
    back_button = Button(rect=(20, MENU_HEIGHT - 70, 150, 50), text="Go Back", bg_color=BROWN,
                         text_color=WHITE, font_size=24, callback=None)
    join_button = Button(rect=(MENU_WIDTH - 170, MENU_HEIGHT - 70, 150, 50), text="Join Game", bg_color=BROWN,
                         text_color=WHITE, font_size=24, callback=None)
    
    ip_box.set_active(True)
    active_box = ip_box

    def attempt_join():
        nonlocal error_message
        ip_text = ip_box.get_text().strip()
        port_text = port_box.get_text().strip()
        if not ip_text or not port_text:
            error_message = "IP and Port cannot be empty."
            return None
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                error_message = "Port must be between 1 and 65535."
                return None
        except ValueError:
            error_message = "Invalid port number."
            return None

        # Perform handshake check.
        success, err = is_server_listening(ip_text, port)
        if not success:
            # If no server is found and we're on localhost, launch the server.
            if auto_start and ip_text == "127.0.0.1" and "No server running" in err:
                print("No server detected; launching server thread.")
                import threading, time
                server_thread = threading.Thread(target=lambda: __import__("server2.server_main").main(), daemon=True)
                server_thread.start()
                time.sleep(1)  # Give the server time to start.
                # Retry handshake.
                success, err = is_server_listening(ip_text, port)
                if not success:
                    error_message = err
                    return None
            else:
                error_message = err
                return None
        return ip_text, port


    font = pygame.font.SysFont("Arial", 20)
    while True:
        screen.fill(CREAM)
        title = font.render("Join Game", True, BROWN)
        screen.blit(title, (MENU_WIDTH // 2 - title.get_width() // 2, 40))
        info = font.render("Click boxes or press [Tab] to switch, [Enter] to confirm", True, BROWN)
        screen.blit(info, (MENU_WIDTH // 2 - info.get_width() // 2, 90))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ip_box.rect.collidepoint(event.pos):
                    ip_box.set_active(True)
                    port_box.set_active(False)
                    active_box = ip_box
                elif port_box.rect.collidepoint(event.pos):
                    port_box.set_active(True)
                    ip_box.set_active(False)
                    active_box = port_box
                elif back_button.rect.collidepoint(event.pos):
                    return None  # Cancel join.
                elif join_button.rect.collidepoint(event.pos):
                    result = attempt_join()
                    if result:
                        return result
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if active_box == ip_box:
                        ip_box.set_active(False)
                        port_box.set_active(True)
                        active_box = port_box
                    else:
                        port_box.set_active(False)
                        ip_box.set_active(True)
                        active_box = ip_box
                elif event.key == pygame.K_RETURN:
                    result = attempt_join()
                    if result:
                        return result
                elif event.key == pygame.K_BACKSPACE:
                    active_box.remove_char()
                else:
                    active_box.add_char(event.unicode)
        
        ip_box.draw(screen, True)
        port_box.draw(screen, True)
        back_button.draw(screen)
        join_button.draw(screen)
        if error_message:
            err_surface = font.render(error_message, True, (255, 0, 0))
            screen.blit(err_surface, (MENU_WIDTH // 2 - err_surface.get_width() // 2, 300))
        pygame.display.flip()
        clock.tick(60)


# run game - back to menu
def run_game(screen, server_ip, server_port):
    # Resize window to game dimensions.
    pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    screen = pygame.display.get_surface()  # Get updated display surface.
    
    clock = pygame.time.Clock()
    assets = load_assets()
    game_manager = ClientGameManager()
    networking = ClientNetworking(server_ip, server_port)
    networking.add_receive_callback(lambda msg: game_manager.handle_update(msg))
    networking.start_receiving()
    
    dragging_cookie = None

    # UI elements for game actions and to return to menu.
    start_button = Button((GAME_WIDTH//2 - 100, GAME_HEIGHT//2 - 25, 200, 50), "Start Game", (0, 128, 0))
    reset_button = Button((GAME_WIDTH//2 - 63, GAME_HEIGHT//1.65 - 25, 120, 35), "Reset", (128, 0, 0))
    back_button = Button((400, 10, 140, 40), "Back To Menu", (200, 0, 0))
    ip_box_text = TextBox((SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 - 375, 275, 40), "Open IP Server: 127.0.0.1")
    port_box_text = TextBox((SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 - 325, 275, 40), "Open Port: 55555" )
    
    # Helper functions used within the game loop.
    def find_top_cookie(mouse_pos, cookies):
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
        font = pygame.font.SysFont(None, 48)
        text_surface = font.render(status_message, True, BROWN)
        text_rect = text_surface.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2))
        screen.blit(text_surface, text_rect)
    
    running = True
    while running:
        current_mouse_pos = list(pygame.mouse.get_pos())

        if hasattr(game_manager, 'server_shutdown') and game_manager.server_shutdown:
            print("Server has shut down, returning to menu")
            running = False
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game_manager.assigned_player_id == 1:
                    networking.send_message({"type": "shutdown"})
                    print("Sent shutdown signal to server")
                    time.sleep(0.5)  # Give time to send before disconnect
                    running = False  # Only need to change running to false if server shuts down.
                    return False
                else:
                    print("QUIT event detected; sending quit message")
                    networking.send_message({"type": "quit"})
                    running = False
                    return False
            if back_button.handle_event(event):
                if game_manager.assigned_player_id == 1:
                    networking.send_message({"type": "shutdown"})
                    print("Sent shutdown signal to server")
                    time.sleep(0.5)  # Give time to send before disconnect
                    running = False  # Only need to change running to false if server shuts down.
                else: # If the client is not also the server, then remove it from client addresses and stop rendering it's plate.
                    print("QUIT event detected; sending quit message")
                    networking.send_message({"type": "quit"})
                    return "Menu"

                return True

            if game_manager.game_state == GameState.LOBBY.value:
                if game_manager.assigned_player_id == 1:
                    if start_button.handle_event(event):
                        networking.send_message({"type": "start_game"})
                        print("Start game message sent")
            elif game_manager.game_state == GameState.GAME_OVER.value:
                if game_manager.assigned_player_id == 1:
                    if reset_button.handle_event(event):
                        networking.send_message({"type": "reset_game"})
                        print("Reset game message sent")
            elif game_manager.game_state == GameState.PLAYING.value:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dragging_cookie = find_top_cookie(current_mouse_pos, game_manager.cookies)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_cookie = None
        
        update_msg = {
            "type": "update",
            "position": current_mouse_pos,
            "dragged_cookie": dragging_cookie
        }
        networking.send_message(update_msg)
        
        render(screen, game_manager, assets, game_manager.assigned_player_id, reset_button)
        if game_manager.game_state == GameState.LOBBY.value:
            if game_manager.assigned_player_id == 1:
                start_button.draw(screen)
                ip_box_text.draw(screen)
                port_box_text.draw(screen)
            else:
                ip_box_text.draw(screen)
                port_box_text.draw(screen)
                draw_status_text(screen, "waiting for players")
        elif game_manager.game_state == GameState.GAME_OVER.value:
            if game_manager.assigned_player_id == 1:
                reset_button.draw(screen)
            else:
                draw_status_text(screen, "game ended - waiting for host")
        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    networking.shutdown()
    pygame.quit()
    return True

# centralized loop within client
def main():
    pygame.init()
    # Set initial window to menu dimensions.
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Cookie Grabber - Client")
    
    while True:
        menu_result = run_main_menu(screen)
        if not menu_result:
            print("Exiting game from menu.")
            break
        mode, server_ip, server_port, user_is_host = menu_result
        
        # If "Start Game" is selected, immediately launch the server.
        if mode == "start":
            import threading, time
            server_thread = threading.Thread(
                target=lambda: __import__("server2.server_main", fromlist=["main"]).main(),
                daemon=True
            )
            server_thread.start()
            for i in range(10):
                ready, _ = is_server_listening(server_ip, server_port)
                if ready:
                    print("✅ Server is ready!")
                    break
                else:
                    print(f"Waiting for server... ({i+1}/10)")
                time.sleep(0.5)
            else:
                print("Server failed to start in time.")
                continue  # Skip starting the client game loop
            
        # Run the client game loop.
        back_to_menu = run_game(screen, server_ip, server_port)
        if not back_to_menu:
            print("Exiting game loop to quit completely.")
            break
        # After game, reset window to menu size.
        print("Returned to menu from game.")
        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()
