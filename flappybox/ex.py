import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
canvas_width = 600
canvas_height = 400
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Text Example")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create a font object
font = pygame.font.Font("pixelFont.ttf", 36)  # You can choose the font and size

# Create a text surface
text_surface = font.render("Hello, Pygame!", True, BLACK, WHITE)

# Set the position of the text
text_rect = text_surface.get_rect(center=(canvas_width // 2, canvas_height // 2))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    canvas.fill(WHITE)

    # Draw the text surface on the canvas
    canvas.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip()

# Quit pygame and the script
pygame.quit()
sys.exit()
