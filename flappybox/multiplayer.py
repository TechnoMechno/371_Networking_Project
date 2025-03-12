import main
import multiGame
import pygame
import leaderboard
import play
import server
import threading
import time
import loading

# Initialize Pygame
pygame.init()

#NOTE PLEASE DO NOT START BOTH MULTIPLAYER CLIENTS AT THE SAME TIME WAIT TILL SERVER IS UP THEN START the other multiplayer client!

# Set up the display
canvas_width = 600
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")


#playercount 
playerCount = 0

# Define colors
WHITE = (255, 255, 255)
GREEN = (105, 129, 54)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

#button MAKE LOOK NICER
font = pygame.font.Font(None, 36)
button_width = 200
button_height = 50

start_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 - 20, button_width, button_height)
start_button_text = font.render("start", True, BLACK)
start_text_position = ((start_button_rect.left + start_button_rect.right - start_button_text.get_width()) // 2, (start_button_rect.top + start_button_rect.bottom - start_button_text.get_height()) // 2)

def multiplayerText():
    singleplayerFont = pygame.font.Font("pixelFont.ttf", 50) 
    singleplayer_text_surface = singleplayerFont.render("Multiplayer", True, WHITE)
    pos = (canvas_width // 2 - singleplayer_text_surface.get_width() // 2, 250)
    canvas.blit(singleplayer_text_surface, pos)

def multi():
  playCheck = True
  while playCheck:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        playCheck = False
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if main.clicked(event.pos, start_button_rect):
          main.drawBackground()
          main.exitText()
          loading.drawMatchText()
          pygame.display.update()
          # Start the server in a separate thread
          if not server.is_server_running():  # Check if server is already running
                    time.sleep(1)
                    print("Starting server...")
                    server_thread = threading.Thread(target=server.serverMain)
                    server_thread.start()
                    time.sleep(5)
          else:
              print("Server is already running.")
          print("Connecting...")
          
          multiGame.game("Multiplayer")
      elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
        play.modes()
    main.drawBackground()
    multiplayerText()
    main.exitText()
    main.drawButton(start_button_rect, start_button_text, start_text_position)
    
    pygame.display.update()
  pygame.quit()


  

if __name__ == "__main__":
  multi()
