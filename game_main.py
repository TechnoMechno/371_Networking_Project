import pygame
import sys
import threading

# Import your main functions for the game logic
from client2 import client_main 
from server2 import server_main
from client2.Button import Button  
from client2.TextBox import TextBox 
# === Pygame Setup ===
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Grabber")

WHITE = (255, 255, 255)
BROWN = (160, 82, 45)
DARK_BROWN = (101, 67, 33)
BLACK = (0, 0, 0)

title_font = pygame.font.SysFont("comicsansms", 48)
button_font = pygame.font.SysFont("comicsansms", 30)

mode_selection = None

# === Menu Button Callbacks ===
def start_game_callback():
    global mode_selection
    mode_selection = "start"

def join_game_callback():
    global mode_selection
    mode_selection = "join"

# === Buttons for Main Menu ===
buttons = [
    Button(rect=(220, 190, 200, 60), text="Start a Game", bg_color=BROWN, 
           text_color=WHITE, font_size=30, callback=start_game_callback),
    Button(rect=(220, 260, 200, 60), text="Join a Game", bg_color=BROWN, 
           text_color=WHITE, font_size=30, callback=join_game_callback)
]

# === MENU LOOP ===
menu_running = True
while menu_running:
    screen.fill(WHITE)
    title_surface = title_font.render("Cookie Grabber", True, DARK_BROWN)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))
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

# === Refactored IP Input Screen Using TextBox Widgets ===
def ip_input_screen():
    clock = pygame.time.Clock()
    blink = True
    blink_timer = 0

    # Create two text boxes: one for the IP and one for the Port.
    ip_box = TextBox(rect=(WIDTH // 2 - 150, 160, 300, 40), text="Enter IP", 
                     font_size=30, bg_color=(220,220,220), text_color=BLACK, 
                     border_color=BLACK, border_width=2)
    port_box = TextBox(rect=(WIDTH // 2 - 150, 220, 300, 40), text="Enter Port", 
                       font_size=30, bg_color=(220,220,220), text_color=BLACK, 
                       border_color=BLACK, border_width=2)

    # Start with the IP box active.
    ip_box.set_active(True)
    active_box = ip_box

    running = True
    while running:
        screen.fill(WHITE)
        # Draw the title and instructions.
        title = button_font.render("Join Game", True, DARK_BROWN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        label = pygame.font.SysFont("Arial", 20).render(
            "Click boxes or press [Tab] to switch, [Enter] to confirm", True, DARK_BROWN)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 90))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if either text box is clicked.
                if ip_box.rect.collidepoint(event.pos):
                    ip_box.set_active(True)
                    port_box.set_active(False)
                    active_box = ip_box
                elif port_box.rect.collidepoint(event.pos):
                    port_box.set_active(True)
                    ip_box.set_active(False)
                    active_box = port_box
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Switch active text box
                    if active_box == ip_box:
                        ip_box.set_active(False)
                        port_box.set_active(True)
                        active_box = port_box
                    else:
                        port_box.set_active(False)
                        ip_box.set_active(True)
                        active_box = ip_box
                elif event.key == pygame.K_RETURN:
                    # Validate and return if correct.
                    ip_text = ip_box.get_text().strip()
                    port_text = port_box.get_text().strip()
                    if ip_text and port_text.isdigit():
                        return ip_text, int(port_text)
                elif event.key == pygame.K_BACKSPACE:
                    active_box.remove_char()
                else:
                    # Only add printable characters.
                    active_box.add_char(event.unicode)

        # Blinking cursor logic.
        blink_timer += clock.get_time()
        if blink_timer > 500:
            blink = not blink
            blink_timer = 0

        # Draw the text boxes.
        ip_box.draw(screen, blink)
        port_box.draw(screen, blink)

        pygame.display.flip()
        clock.tick(60)

# === RUN GAME ===
if mode_selection == "start":
    print("Starting as server + client")
    # Run the server in a thread
    server_thread = threading.Thread(target=server_main.main, daemon=True)
    server_thread.start()
    # Run the client in the main thread
    client_main.main()

elif mode_selection == "join":
    print("Joining as client only")
    ip, port = ip_input_screen()
    print(f"Connecting to {ip}:{port}")
    client_main.SERVER_IP = ip
    client_main.SERVER_PORT = port
    client_main.main()

pygame.quit()
sys.exit()
