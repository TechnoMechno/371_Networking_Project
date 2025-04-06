import pygame
import os
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE, COOKIE_SIZE, CREAM, BROWN, WHITE, BLACK

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
    # Renders the central plate on the given screen.
    pos = central_plate.position
    radius = central_plate.radius

    # Scale the plate image to the desired size (width and height = 2 * radius)
    scaled_plate = pygame.transform.scale(plate_img, (radius * 2, radius * 2))
    # Create a rect with the scaled image, centered at the plate's position.
    rect = scaled_plate.get_rect(center=(int(pos[0]), int(pos[1])))
    # Blit the scaled plate onto the screen.
    screen.blit(scaled_plate, rect)

def draw_scoreboard(screen, scoreboard):
    """
    Draws the scoreboard on the screen.
    Each entry in the scoreboard dictionary should contain:
      - "player": a label (e.g., "Player 1")
      - "score": the player's score
      - "position": a dict with 'x' and 'y' for where to draw the text.
    """
    # Initialize a font object
    font = pygame.font.SysFont(None, 36)
    for key, data in scoreboard.items():
        # Construct the score text
        text = f"{data['player']}, Score: {data['score']}"
        # Use the provided coordinates from scoreboard data
        pos = data['position']
        text_surface = font.render(text, True, BROWN)
        screen.blit(text_surface, (pos["x"], pos["y"]))

def render(screen, game_state, assets, assigned_player_id):
    """
    Renders the full game state:
      - The central plate.
      - Cookies.
      - Players' plates.
      - Player cursors.
      - Scoreboard.
    """

    regular_img, star_img, plate_img = assets
    screen.fill(BACKGROUND_COLOR)
    
    # Render central plate.
    draw_central_plate(screen, game_state.central_plate, plate_img)
    
     # Render players' plates.
    for pid, player in game_state.players.items():
        plate_data = player.get("plate")
        print(f"Player {pid} plate data:", plate_data) 
        plate_data = player.get("plate")
        if plate_data:
            pos = plate_data.get("plate_position", [0, 0])
            radius = plate_data.get("plate_radius", 150)
            scaled_plate = pygame.transform.scale(plate_img, (radius * 2, radius * 2))
            rect = scaled_plate.get_rect(center=(int(pos[0]), int(pos[1])))
            screen.blit(scaled_plate, rect)
            
    # Render cookies.
    for cid, cookie in game_state.cookies.items():
        pos = cookie.get("position", [0, 0])
        ctype = cookie.get("cookie_type", "regular")
        img = regular_img if ctype == "regular" else star_img
        rect = img.get_rect(center=(int(pos[0]), int(pos[1])))
        screen.blit(img, rect)
    
    # Render player cursors.
    for pid, player in game_state.players.items():
        pos = player.get("mouse_pos", [0, 0])
        # Highlight the assigned player's cursor in red; others in green.
        color = (255, 0, 0) if str(pid) == str(assigned_player_id) else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 5)
    
    # Render the scoreboard if available.
    if hasattr(game_state, "scoreboard") and game_state.scoreboard:
        draw_scoreboard(screen, game_state.scoreboard)
