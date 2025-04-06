import pygame
import sys
import threading
from server2 import server_main
from client2.client_main import main as client_main
from client2.Button import Button  
from client2.TextBox import TextBox
from game_code.config import CREAM, BROWN, WHITE, BLACK

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Grabber")

# --- Fonts & Assets ---
title_font = pygame.font.SysFont("comicsansms", 64)
button_font = pygame.font.SysFont("comicsansms", 30)
try:
    cookie_img = pygame.image.load("Assets/cookie.png").convert_alpha()
    cookie_img = pygame.transform.scale(cookie_img, (64, 64))
except pygame.error as e:
    print("Error loading cookie asset:", e)
    cookie_img = None

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

# --- Main Menu Function ---
def run_main_menu():
    mode_selection = None
    buttons = [
        Button(rect=(200, 200, 200, 60), text="Start a Game", bg_color=BROWN, 
               text_color=WHITE, font_size=30, callback=lambda: set_mode("start")),
        Button(rect=(200, 280, 200, 60), text="Join a Game", bg_color=BROWN, 
               text_color=WHITE, font_size=30, callback=lambda: set_mode("join"))
    ]
    
    def set_mode(selection):
        nonlocal mode_selection
        mode_selection = selection

    clock = pygame.time.Clock()
    while mode_selection is None:
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
        clock.tick(60)
    
    # If the user chose to join, prompt for IP/port:
    if mode_selection == "join":
        result = ip_input_screen()
        if result is None:
            # If user cancels, restart menu
            return run_main_menu()
        else:
            server_ip, server_port = result
    else:
        # For "start", assume hosting on localhost
        server_ip, server_port = "127.0.0.1", 55555
    return mode_selection, server_ip, server_port

# --- IP Input Screen (for joining a game) ---
def ip_input_screen():
    clock = pygame.time.Clock()
    error_message = None
    ip_box = TextBox(rect=(WIDTH // 2 - 150, 160, 300, 40), text="Enter IP", 
                     font_size=30, bg_color=WHITE, text_color=BLACK, 
                     border_color=BROWN, border_width=2)
    port_box = TextBox(rect=(WIDTH // 2 - 150, 220, 300, 40), text="Enter Port", 
                       font_size=30, bg_color=WHITE, text_color=BLACK, 
                       border_color=BROWN, border_width=2)
    back_button = Button(rect=(20, HEIGHT - 70, 150, 50), text="Go Back", bg_color=BROWN, 
                         text_color=WHITE, font_size=24, callback=None)
    join_button = Button(rect=(WIDTH - 170, HEIGHT - 70, 150, 50), text="Join Game", bg_color=BROWN, 
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
        # Simple IP/port validation (expand as needed)
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                error_message = "Port must be between 1 and 65535."
                return None
        except ValueError:
            error_message = "Invalid port number."
            return None
        return ip_text, port

    while True:
        screen.fill(CREAM)
        if cookie_img is not None:
            for pos in cookie_positions:
                screen.blit(cookie_img, pos)
        title = button_font.render("Join Game", True, BROWN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        info = pygame.font.SysFont("Arial", 20).render(
            "Click boxes or press [Tab] to switch, [Enter] to confirm", True, BROWN)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 90))
        
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
                    return None  # Cancel join; return to menu
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
            err_surface = pygame.font.SysFont("Arial", 20).render(error_message, True, (255, 0, 0))
            screen.blit(err_surface, (WIDTH // 2 - err_surface.get_width() // 2, 300))
        
        pygame.display.flip()
        clock.tick(60)

# --- Game Loop Wrapper ---
def run_game(server_ip, server_port):
    pygame.display.set_mode((WIDTH,HEIGHT))
    back_to_menu = client_main(server_ip, server_port)
    return back_to_menu

# --- Centralized Main Loop ---
def main():
    while True:
        # Show the main menu and get a game mode and connection info.
        result = run_main_menu()
        if not result:
            break  # exit if menu cancelled
        mode, server_ip, server_port = result

        # If hosting, start the server thread
        if mode == "start":
            print("Starting as server + client")
            server_thread = threading.Thread(target=server_main.main, daemon=True)
            server_thread.start()
        else:
            print("Joining as client only")
        
        # Run the game loop.
        # client_main should include a mechanism (e.g., a "Back to Menu" button)
        # that, when activated, breaks out of its loop and returns True.
        back_to_menu = run_game(server_ip, server_port)
        if not back_to_menu:
            break  # if the game signals to exit completely, break out
        # Otherwise, loop back to show the main menu again.

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
