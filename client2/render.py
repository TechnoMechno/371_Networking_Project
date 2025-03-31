import pygame
import os
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE, COOKIE_SIZE

def load_assets():
    # Load and scale assets after display is initialized.
    base_path = os.path.dirname(os.path.abspath(__file__))
    def load_image(path):
        return pygame.image.load(os.path.join(base_path, "..", "game_code", path)).convert_alpha()
    regular_img = load_image(REGULAR_COOKIE_IMAGE)
    star_img = load_image(STAR_COOKIE_IMAGE)
    plate_img = load_image(PLATE_IMAGE)
    regular_img = pygame.transform.scale(regular_img, (COOKIE_SIZE, COOKIE_SIZE))
    star_img = pygame.transform.scale(star_img, (COOKIE_SIZE, COOKIE_SIZE))
    return regular_img, star_img, plate_img

def draw_central_plate(screen, central_plate, plate_img):
    #Renders the central plate on the given screen.
    pos = central_plate.position
    radius = central_plate.radius

    # Scale the plate image to the desired size (width and height = 2 * radius)
    scaled_plate = pygame.transform.scale(plate_img, (radius * 2, radius * 2))
    # Create a rect with the scaled image, centered at the plate's position.
    rect = scaled_plate.get_rect(center=(int(pos[0]), int(pos[1])))
    # Blit the scaled plate onto the screen.
    screen.blit(scaled_plate, rect)

def render(screen, game_state, assets, assigned_player_id):
    regular_img, star_img, plate_img = assets
    screen.fill(BACKGROUND_COLOR)
    # Render central plate
    
    draw_central_plate(screen, game_state.central_plate, plate_img)
    
    # Render cookies:
    for cid, cookie in game_state.cookies.items():
        pos = cookie.get("position", [0, 0])
        ctype = cookie.get("cookie_type", "regular")
        img = regular_img if ctype == "regular" else star_img
        rect = img.get_rect(center=(int(pos[0]), int(pos[1])))
        screen.blit(img, rect)
    # Render players' plates:
    for pid, player in game_state.players.items():
        plate_data = player.get("plate")
        if plate_data:
            pos = plate_data.get("plate_position", [0, 0])
            radius = plate_data.get("plate_radius", 150)
            scaled_plate = pygame.transform.scale(plate_img, (radius * 2, radius * 2))
            rect = scaled_plate.get_rect(center=(int(pos[0]), int(pos[1])))
            screen.blit(scaled_plate, rect)
    # Render player cursors:
    for pid, player in game_state.players.items():
        pos = player.get("mouse_pos", [0, 0])
        color = (255, 0, 0) if str(pid) == str(assigned_player_id) else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 5)
    pygame.display.flip()