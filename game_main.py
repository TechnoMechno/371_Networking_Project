import pygame
import sys
import threading
import socket
import ipaddress  # For IP validation
import errno

# Import your main functions for the game logic
from client2 import client_main 
from server2 import server_main
from client2.Button import Button  
from client2.TextBox import TextBox
from game_code.config import CREAM, BROWN, WHITE, BLACK 

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Grabber")

# --- Fonts ---
title_font = pygame.font.SysFont("comicsansms", 64)
button_font = pygame.font.SysFont("comicsansms", 30)

# --- Load Cookie Asset ---
try:
    cookie_img = pygame.image.load("Assets/cookie.png").convert_alpha()
    cookie_img = pygame.transform.scale(cookie_img, (64, 64))
except pygame.error as e:
    print("Error loading cookie asset:", e)
    cookie_img = None

# --- Predefined Cookie Positions ---
cookie_positions = []
if cookie_img is not None:
    cookie_positions = [
        (30, 30),                                      
        (WIDTH - 50 - 64, 30),
        (30, HEIGHT - 30 - 64),
        (WIDTH - 30 - 64, HEIGHT - 30 - 64),
        (WIDTH//2 - 32, HEIGHT / 2 - 50),
        (10, HEIGHT//2 - 40),
        (WIDTH - 150, HEIGHT//2 - 24)
    ]

# --- Global variable for menu selection ---
mode_selection = None

# --- Handshake Function for UDP ---
def is_server_listening(ip_address, port):
    """
    Send a UDP 'PING' message and expect a 'PONG' reply.
    Returns True if the correct response is received within the timeout, else False.
    """
    test_message = "PING"
    expected_response = "PONG"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)  # 1-second timeout for a response
    try:
        sock.sendto(test_message.encode(), (ip_address, port))
        data, addr = sock.recvfrom(1024)
        if data.decode().strip() == expected_response:
            return True
    except socket.timeout:
        return False
    except Exception as e:
        print("Handshake error:", e)
        return False
    finally:
        sock.close()
    return False

# --- Main Menu Loop Function ---
def main_menu():
    global mode_selection
    mode_selection = None
    buttons = [
        Button(rect=(200, 200, 200, 60), text="Start a Game", bg_color=BROWN, 
               text_color=WHITE, font_size=30, callback=lambda: set_mode("start")),
        Button(rect=(200, 280, 200, 60), text="Join a Game", bg_color=BROWN, 
               text_color=WHITE, font_size=30, callback=lambda: set_mode("join"))
    ]
    
    menu_running = True
    while menu_running:
        screen.fill(CREAM)
        if cookie_img is not None:
            for pos in cookie_positions:
                screen.blit(cookie_img, pos)
        title_surface = title_font.render("COOKIE GRABBER", True, BROWN)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()
        if mode_selection is not None:
            menu_running = False

def set_mode(selection):
    global mode_selection
    mode_selection = selection

# --- IP and Port Validation Functions ---
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_port(port):
    try:
        port = int(port)
        return 1 <= port <= 65535
    except ValueError:
        return False

# --- IP Input Screen (for joining a game) ---
def ip_input_screen():
    clock = pygame.time.Clock()
    blink = True
    blink_timer = 0
    error_message = None  # For error messages

    # Create text boxes for IP and Port
    ip_box = TextBox(rect=(WIDTH // 2 - 150, 160, 300, 40), text="Enter IP", 
                     font_size=30, bg_color=WHITE, text_color=BLACK, 
                     border_color=BROWN, border_width=2)
    port_box = TextBox(rect=(WIDTH // 2 - 150, 220, 300, 40), text="Enter Port", 
                       font_size=30, bg_color=WHITE, text_color=BLACK, 
                       border_color=BROWN, border_width=2)
    
    # Buttons for navigation
    back_button = Button(rect=(20, HEIGHT - 70, 150, 50), text="Go Back", bg_color=BROWN, 
                         text_color=WHITE, font_size=24, callback=None)
    join_button = Button(rect=(WIDTH / 2 + 130, HEIGHT - 70, 150, 50), text="Join Game", bg_color=BROWN, 
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
        if not is_valid_ip(ip_text):
            error_message = "Invalid IP address."
            return None
        if not port_text.isdigit() or not is_valid_port(port_text):
            error_message = "Invalid port number."
            return None
        # Use UDP handshake to check for server availability
        if not is_server_listening(ip_text, int(port_text)):
            error_message = "No server running on IP: " + ip_text + " and port: " + port_text
            return None
        return ip_text, int(port_text)

    running = True
    while running:
        screen.fill(CREAM)
        if cookie_img is not None:
            for pos in cookie_positions:
                screen.blit(cookie_img, pos)
        
        title = button_font.render("Join Game", True, BROWN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        label = pygame.font.SysFont("Arial", 20).render(
            "Click boxes or press [Tab] to switch, [Enter] to confirm", True, BROWN)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 90))
        
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
                    return None  # Go back to main menu
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
        
        blink_timer += clock.get_time()
        if blink_timer > 500:
            blink = not blink
            blink_timer = 0

        ip_box.draw(screen, blink)
        port_box.draw(screen, blink)
        back_button.draw(screen)
        join_button.draw(screen)
        
        if error_message:
            error_surface = pygame.font.SysFont("Arial", 20).render(error_message, True, (255, 0, 0))
            screen.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, 300))
        
        pygame.display.flip()
        clock.tick(60)

# --- Main Program Loop ---
while True:
    main_menu()
    if mode_selection == "start":
        print("Starting as server + client")
        server_thread = threading.Thread(target=server_main.main, daemon=True)
        server_thread.start()
        client_main.main()
        break
    elif mode_selection == "join":
        print("Joining as client only")
        result = ip_input_screen()
        if result is None:
            mode_selection = None
            continue
        else:
            ip, port = result
            print(f"Connecting to {ip}:{port}")
            client_main.SERVER_IP = ip
            client_main.SERVER_PORT = port
            client_main.main()
            break

pygame.quit()
sys.exit()
