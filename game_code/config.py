# config.py
import os
import enum
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (255,245,211)
COOKIE_SIZE = 100  # Changed from PANCAKE_SIZE
COOKIE_COUNT = 3
INITIAL_COOKIE_POS = [(400, 500), (400, 450), (400, 400)]  # Changed from INITIAL_PANCAKE_POS
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "Assets")
REGULAR_COOKIE_IMAGE = os.path.join(ASSETS_DIR, "cookie.png")
STAR_COOKIE_IMAGE = os.path.join(ASSETS_DIR, "starcookie.png")
PLATE_IMAGE = os.path.join(ASSETS_DIR, "plate.png")
HOST = "0.0.0.0"
UDP_PORT = 55555

# COLOURS
CREAM = (255, 241, 208)          # Warm cream background
BROWN = (101, 67, 33)            # Deep brown for title and buttons
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class GameState(enum.Enum):
    LOBBY = 1
    PLAYING = 2
    GAME_OVER = 3