import main
import game
import pygame
import leaderboard
import play
import multiplayer

# Initialize Pygame
pygame.init()

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
start_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 - 40, button_width, button_height)

start_button_text = font.render("start", True, BLACK)
start_text_position = ((start_button_rect.left + start_button_rect.right - start_button_text.get_width()) // 2, (start_button_rect.top + start_button_rect.bottom - start_button_text.get_height()) // 2)

leaderboards_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 + button_height - 20, button_width, button_height)
leaderboards_button_text = font.render("leaderboards", True, BLACK)
leaderboards_text_position = ((leaderboards_button_rect.left + leaderboards_button_rect.right - leaderboards_button_text.get_width()) // 2, (leaderboards_button_rect.top + leaderboards_button_rect.bottom - leaderboards_button_text.get_height()) // 2)

def singleplayerText():
    singleplayerFont = pygame.font.Font("pixelFont.ttf", 50) 
    singleplayer_text_surface = singleplayerFont.render("Singleplayer", True, WHITE)
    pos = (canvas_width // 2 - singleplayer_text_surface.get_width() // 2, 250)
    canvas.blit(singleplayer_text_surface, pos)

def single():
  playCheck = True
  
  while playCheck:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        playCheck = False
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if main.clicked(event.pos, start_button_rect):
          game.game("Singleplayer")
        elif main.clicked(event.pos, leaderboards_button_rect):
          leaderboard.board()
      elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
        play.modes()
    main.drawBackground()
    singleplayerText()
    main.exitText()
    main.drawButton(start_button_rect, start_button_text, start_text_position)
    main.drawButton(leaderboards_button_rect, leaderboards_button_text, leaderboards_text_position)
    
    pygame.display.update()
  pygame.quit()


  

if __name__ == "__main__":
  single()
