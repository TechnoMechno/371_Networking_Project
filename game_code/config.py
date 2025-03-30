# config.py
import os
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (255,245,211)
COOKIE_SIZE = 100  # Changed from PANCAKE_SIZE
INITIAL_COOKIE_POS = [(400, 500), (400, 450), (400, 400)]  # Changed from INITIAL_PANCAKE_POS
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "Assets")
REGULAR_COOKIE_IMAGE = os.path.join(ASSETS_DIR, "cookie.png")
STAR_COOKIE_IMAGE = os.path.join(ASSETS_DIR, "starcookie.png")
PLATE_IMAGE = os.path.join(ASSETS_DIR, "plate.png")
HOST = "0.0.0.0"
UDP_PORT = 5555