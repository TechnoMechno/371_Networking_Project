import main
import game
import pygame
import server
import client_server
import leaderboard
import multiplayer
import singleplayer

# Initialize Pygame
pygame.init()

# player count 
playercount = 0

# Set up the display
canvas_width = 600
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")

# Define colors
WHITE = (255, 255, 255)
GREEN = (105, 129, 54)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

#button MAKE LOOK NICER
font = pygame.font.Font(None, 36)
button_width = 200
button_height = 50

single_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 - 40, button_width, button_height)
single_button_text = font.render("singleplayer", True, BLACK)
single_text_position = ((single_button_rect.left + single_button_rect.right - single_button_text.get_width()) // 2, (single_button_rect.top + single_button_rect.bottom - single_button_text.get_height()) // 2)

multi_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 + button_height - 20, button_width, button_height)
multi_button_text = font.render("multiplayer", True, BLACK)
multi_text_position = ((multi_button_rect.left + multi_button_rect.right - multi_button_text.get_width()) // 2, (multi_button_rect.top + multi_button_rect.bottom - multi_button_text.get_height()) // 2)

def modesText():
    modesFont = pygame.font.Font("pixelFont.ttf", 50) 
    modes_text_surface = modesFont.render("Modes", True, WHITE)
    pos = (canvas_width // 2 - modes_text_surface.get_width() // 2, 250)
    canvas.blit(modes_text_surface, pos)


def modes():

  choosingMode = True
  
  while choosingMode:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        choosingMode = False
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if main.clicked(event.pos, single_button_rect):
          singleplayer.single()
        elif main.clicked(event.pos, multi_button_rect):   
          multiplayer.multi()
      elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
        main.menu()
    main.drawBackground()
    modesText()
    main.exitText()
    main.drawButton(single_button_rect, single_button_text, single_text_position)
    main.drawButton(multi_button_rect, multi_button_text, multi_text_position)
    pygame.display.update()
  pygame.quit()

if __name__ == "__main__":
  modes()
