import pygame
import os
from game_code.config import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, REGULAR_COOKIE_IMAGE, STAR_COOKIE_IMAGE, PLATE_IMAGE, COOKIE_SIZE, CREAM, BROWN, WHITE, BLACK

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

def draw_end_scoreboard(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        scoreboard_width = 400
        scoreboard_height = 300
        scoreboard_x = (SCREEN_WIDTH - scoreboard_width) // 2
        scoreboard_y = (SCREEN_HEIGHT - scoreboard_height) // 2
        
        pygame.draw.rect(self.screen, (255, 255, 255), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height), 2)
        
        font_title = pygame.font.SysFont('Arial', 28, bold=True)
        title = font_title.render("Game Over", True, (0, 0, 0))
        self.screen.blit(title, (scoreboard_x + (scoreboard_width - title.get_width()) // 2, 
                                  scoreboard_y + 20))
        
        sorted_players = sorted(self.players, key=lambda player: player.score, reverse=True)
        winner = sorted_players[0]
        
        font_winner = pygame.font.SysFont('Arial', 24)
        winner_text = font_winner.render(f"Winner: {winner.name}", True, (0, 0, 0))
        self.screen.blit(winner_text, (scoreboard_x + (scoreboard_width - winner_text.get_width()) // 2, 
                                        scoreboard_y + 60))
        
        font_scores = pygame.font.SysFont('Arial', 20)
        for i, player in enumerate(sorted_players):
            text = font_scores.render(f"{player.name}: {player.score} points", True, (0, 0, 0))
            self.screen.blit(text, (scoreboard_x + 50, scoreboard_y + 100 + i * 30))
        
        font_restart = pygame.font.SysFont('Arial', 16)
        restart_text = font_restart.render("Click Restart to play again", True, (0, 0, 0))
        self.screen.blit(restart_text, (scoreboard_x + (scoreboard_width - restart_text.get_width()) // 2, 
                                        scoreboard_y + scoreboard_height - 40))

def render(screen, game_state, assets, assigned_player_id, reset_button):
    """
    Renders the full game state:
      - The central plate.
      - Cookies.
      - Players' plates.
      - Player cursors.
      - Scoreboard.
    """
    # Scoreboard box
    scoreboard_width = 400
    scoreboard_height = 300
    scoreboard_x = (SCREEN_WIDTH - scoreboard_width) // 2
    scoreboard_y = (SCREEN_HEIGHT - scoreboard_height) // 2

    regular_img, star_img, plate_img = assets
    screen.fill(BACKGROUND_COLOR)
    
    # Render central plate.
    draw_central_plate(screen, game_state.central_plate, plate_img)
    
     # Render players' plates and outline
    for pid, player in game_state.players.items():
        plate_data = player.get("plate")
        if plate_data:
            pos = plate_data.get("plate_position", [0, 0])
            radius = plate_data.get("plate_radius", 150)
            scaled_plate = pygame.transform.scale(plate_img, (radius * 2, radius * 2))
            rect = scaled_plate.get_rect(center=(int(pos[0]), int(pos[1])))
            screen.blit(scaled_plate, rect)
            # draw outline of the local player
            if str(pid) == str(assigned_player_id):
                player_color = tuple(player.get("color", [255, 255, 255]))
                pygame.draw.circle(screen, player_color, (int(pos[0]), int(pos[1])), radius, 7)

    # Render cookies.
    for cid, cookie in game_state.cookies.items():
        pos = cookie.get("position", [0, 0])
        ctype = cookie.get("cookie_type", "regular")
        img = regular_img if ctype == "regular" else star_img
        rect = img.get_rect(center=(int(pos[0]), int(pos[1])))
        screen.blit(img, rect)
    
    # Render player cursors using their color.
    for pid, player in game_state.players.items():
        pos = player.get("mouse_pos", [0, 0])
        player_color = tuple(player.get("color", [255, 255, 255]))  # Use the player's color
        pygame.draw.circle(screen, player_color, (int(pos[0]), int(pos[1])), 5)
    
    # Render the scoreboard if available.
    if hasattr(game_state, "scoreboard") and game_state.scoreboard:
        draw_scoreboard(screen, game_state.scoreboard)

    # print("[DEBUG] Entered render(). Current state:", game_state.game_state)

    if game_state.game_state == GameState.GAME_OVER.value:

        # print("[DEBUG] GAME_OVER block reached. Drawing scoreboard.")
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (255, 255, 255), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height))
        pygame.draw.rect(screen, (0, 0, 0), 
                         (scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height), 2)

        # "Game Over" title
        font_title = pygame.font.SysFont('Arial', 32, bold=True)
        title = font_title.render("Game Over", True, (0, 0, 0))
        screen.blit(title, (scoreboard_x + (scoreboard_width - title.get_width()) // 2, 
                            scoreboard_y + 20))

        # Sort players by score
        sorted_players = sorted(game_state.players.items(), key=lambda p: p[1]["score"], reverse=True)

        # Show scores
        font_scores = pygame.font.SysFont('Arial', 22)
        for i, (pid, player) in enumerate(sorted_players):
            text = font_scores.render(f'{player["name"]}: {player["score"]} pts', True, (0, 0, 0))
            screen.blit(text, (scoreboard_x + 40, scoreboard_y + 80 + i * 30))

        if str(assigned_player_id) == "1":
            print("[DEBUG] host player.")
            # "Press R to Restart"
            font_restart = pygame.font.SysFont('Arial', 20)
            restart_text = font_restart.render("or Press R to restart", True, (50, 50, 50))
            screen.blit(restart_text, (scoreboard_x + (scoreboard_width - restart_text.get_width()) // 2, scoreboard_y + scoreboard_height - 40))
            reset_button.draw(screen)
        else:
            font_status = pygame.font.SysFont(None, 28)
            waiting_text = font_status.render("Waiting for host to restart...", True, (0, 0, 0))
            screen.blit(waiting_text, (
                (SCREEN_WIDTH - waiting_text.get_width()) // 2,
                (SCREEN_HEIGHT + scoreboard_height) // 2 - 40
            ))
