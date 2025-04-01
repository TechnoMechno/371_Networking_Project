import pygame
import sys
import threading

# Import the main functions instead of classes
from client2 import client_main 
from server2 import server_main

# === Pygame Setup ===
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Grabber")

WHITE = (255, 255, 255)
BROWN = (160, 82, 45)
DARK_BROWN = (101, 67, 33)
HOVER_COLOR = (200, 140, 100)
BLACK = (0, 0, 0)

title_font = pygame.font.SysFont("comicsansms", 48)
button_font = pygame.font.SysFont("comicsansms", 30)

mode_selection = None

# === Button ===
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = HOVER_COLOR if self.rect.collidepoint(mouse_pos) else BROWN
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = button_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# === Menu Button Callbacks ===
def start_game_callback():
    global mode_selection
    mode_selection = "start"

def join_game_callback():
    global mode_selection
    mode_selection = "join"

# === Buttons ===
buttons = [
    Button("Start a Game", WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 50, start_game_callback),
    Button("Join a Game", WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50, join_game_callback),
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

def ip_input_screen():
    input_active = True
    ip_input = ""
    port_input = "5555" 
    
    font = pygame.font.SysFont("comicsansms", 30)
    label_font = pygame.font.SysFont("Arial", 20)

    is_typing_ip = True
    ip_box = pygame.Rect(WIDTH // 2 - 150, 160, 300, 40)
    port_box = pygame.Rect(WIDTH // 2 - 150, 220, 300, 40)

    clock = pygame.time.Clock()
    blink = True
    blink_timer = 0

    while input_active:
        screen.fill(WHITE)
        title = font.render("Join Game", True, DARK_BROWN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        label = label_font.render("Click boxes or press [Tab] to switch, [Enter] to confirm", True, DARK_BROWN)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 90)) 

        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                if ip_box.collidepoint(event.pos):
                    is_typing_ip = True
                elif port_box.collidepoint(event.pos):
                    is_typing_ip = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    is_typing_ip = not is_typing_ip
                elif event.key == pygame.K_RETURN:
                    if ip_input.strip() and port_input.strip().isdigit():
                        return ip_input.strip(), int(port_input.strip())
                elif event.key == pygame.K_BACKSPACE:
                    if is_typing_ip:
                        ip_input = ip_input[:-1]
                    else:
                        port_input = port_input[:-1]
                else:
                    if is_typing_ip:
                        ip_input += event.unicode
                    elif event.unicode.isdigit():
                        port_input += event.unicode

        # Input box colors
        ip_color = (200, 200, 255) if is_typing_ip else (220, 220, 220)
        port_color = (200, 200, 255) if not is_typing_ip else (220, 220, 220)

        # Draw boxes
        pygame.draw.rect(screen, ip_color, ip_box, border_radius=6)
        pygame.draw.rect(screen, port_color, port_box, border_radius=6)
        pygame.draw.rect(screen, BLACK, ip_box, 2, border_radius=6)
        pygame.draw.rect(screen, BLACK, port_box, 2, border_radius=6)

        # Blinking cursor logic
        blink_timer += clock.get_time()
        if blink_timer > 500:
            blink = not blink
            blink_timer = 0

        # Render text with blinking cursor
        ip_display = ip_input if ip_input else "Enter IP"
        if is_typing_ip and blink:
            ip_display += "|"
        ip_text = font.render(ip_display, True, BLACK)
        screen.blit(ip_text, (ip_box.x + 10, ip_box.y + 5))

        port_display = port_input if port_input else "Enter Port"
        if not is_typing_ip and blink:
            port_display += "|"
        port_text = font.render(port_display, True, BLACK)
        screen.blit(port_text, (port_box.x + 10, port_box.y + 5))

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
    #run_client()

pygame.quit()
sys.exit()

