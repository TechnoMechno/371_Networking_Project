import pygame
import sys
from ui import draw_interface, draw_plate, draw_cookies

pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Grabber")

# Colors
WHITE = (255, 255, 255)
BROWN = (160, 82, 45)
DARK_BROWN = (101, 67, 33)
HOVER_COLOR = (200, 140, 100)
BLACK = (0, 0, 0)

# Fonts
title_font = pygame.font.SysFont("comicsansms", 48)
button_font = pygame.font.SysFont("comicsansms", 30)

# Game state
MENU = "menu"
GAME = "game"
current_state = MENU

# Button class
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

# Placeholder player/plate classes
class DummyPlayer:
    def __init__(self, name, score):
        self.name = name
        self.score = score

class DummyPlate:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        self.radius = radius

# Dummy data for testing ui.py
dummy_players = [DummyPlayer("Player1", 5), DummyPlayer("Player2", 3)]
dummy_plates = [DummyPlate(150, 100), DummyPlate(450, 100)]

# Callbacks
def start_game():
    global current_state
    current_state = GAME

def join_game():
    print("Joining a game... (not implemented yet)")

# Menu buttons
buttons = [
    Button("Start a Game", WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 50, start_game),
    Button("Join a Game", WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50, join_game),
]

# Main loop
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == MENU:
            for button in buttons:
                button.handle_event(event)

    if current_state == MENU:
        # Draw menu
        title_surface = title_font.render("Cookie Grabber", True, DARK_BROWN)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title_surface, title_rect)

        for button in buttons:
            button.draw(screen)

    elif current_state == GAME:
        # Placeholder game screen using ui.py
        draw_plate(screen)
        draw_interface(screen, dummy_players, dummy_plates)

    pygame.display.flip()

pygame.quit()
sys.exit()
