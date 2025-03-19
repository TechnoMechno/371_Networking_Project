import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pygame
from ui import draw_plate, draw_pancakes, draw_scores
from game import Game  

def run_cookie_game(get_score, send_cookie, send_quit):
    """
    Runs the cookie game UI.

    Parameters:
      get_score: A function returning the current score.
      send_cookie: A function to call when SPACE is pressed.
      send_quit: A function to call when QUIT (or ESC/Q) is pressed.
    """
    pygame.init()
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    send_cookie()
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    send_quit()
                    running = False

        draw_plate(game.screen)
        draw_pancakes(game.screen, game.pancakes)
        draw_scores(game.screen, get_score())
        pygame.display.flip()
        game.clock.tick(60)
    pygame.quit()
