import pygame
import sys
import socket
import json
import threading
import ipaddress
import time

# Import configuration and supporting modules.
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, CREAM, BROWN, WHITE, BLACK, GameState
from render import load_assets, render
from client_networking import ClientNetworking
from client_gameManager import ClientGameManager
from Button import Button
from TextBox import TextBox

# Define dimensions for menu and game screens.
MENU_WIDTH, MENU_HEIGHT = 600, 400
GAME_WIDTH, GAME_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT

##############################################
# HANDSHAKE FUNCTION (PING / PONG)
##############################################
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
def run_main_menu(screen):
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
        result = ip_input_screen(screen)
        if result is None:
            return run_main_menu(screen)  # Restart menu if join cancelled.
        else:
            server_ip, server_port = result
    else:
        # For "start", assume hosting on localhost.
        server_ip, server_port = "127.0.0.1", 55555
    return mode_selection, server_ip, server_port

##############################################
# IP INPUT SCREEN (for JOIN mode)
##############################################
def ip_input_screen(screen):
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


##############################################
# CENTRALIZED MAIN LOOP (within client)
##############################################
def main():
    pygame.init()
    # Set initial window to menu dimensions.
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Cookie Grabber - Client")
    
    while True:
        menu_result = run_main_menu(screen)
        if not menu_result:
            break
        mode, server_ip, server_port = menu_result
        
        # If starting the game, you might also want to launch the server.
        # (The client code assumes that if you "start" you host on localhost.)
        if mode == "start":
            # You could optionally launch the server here.
            server_thread = threading.Thread(target=lambda: __import__("server2").server_main.main(), daemon=True)
            server_thread.start()
        
        # Run game loop (window resizes to game dimensions inside run_game).
        back_to_menu = run_game(screen, server_ip, server_port)
        if not back_to_menu:
            break
        # After game, reset window to menu size.
        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
