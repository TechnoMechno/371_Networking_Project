import random
from random import randint
import pygame 
import main
import leaderboard
import client_server
import threading
import server
import time
import displayMatchResult
# Initialize Pygame
pygame.init()

#score
score = 0

# Set up the display
canvas_width = 600
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")

# Define colors
GREEN = (105, 129, 54)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Initialize bird
bird = {
  'x': 50,
  'y': ((canvas_height / 2)) - (15),
  'width': 40,
  'height': 40,
  'velocityX': 1,
  'velocityY': 1,
  'gravity': 4,
  'jump': -50
}

# #cat
# cat_original = pygame.image.load("nyan-cat.gif")
# target_size = (bird['width'],bird['height'])
# cat = pygame.transform.scale(cat_original, target_size)

# Initialize pipe
pipe_height = 300
pipe_width = 50
pipeX = 600
y1 = 0
y2 = canvas_height - pipe_height
pipe = []

# SOME MORE GLOBAL VARIABLES
# initialization of acceleration of bird
acceleration = 0
# delays bird acceleration like in normal flappy bird
bird_mvt_delay = 0
add_pipe_interval = 120  # Add a new pipe every 120 frames

#score count
def scoreCountText():
    global score 
    scoreCountFont = pygame.font.Font("exitfont.ttf", 40) 
    scoreCount_text_surface = scoreCountFont.render(str(score), True, main.WHITE)
    scoreCount_pos = (canvas_width // 2 - scoreCount_text_surface.get_width() // 2, 75)
    canvas.blit(scoreCount_text_surface, scoreCount_pos)
def getScore():
  return score

def gameOverText():
    global score

    text = "Game over with score: " + str(score)

    gameOverFont = pygame.font.Font("exitfont.ttf", 40) 
    gameOver_text_surface = gameOverFont.render(str(text), True, main.WHITE)
    gameOver_pos = (canvas_width // 2 - gameOver_text_surface.get_width() // 2, 125)
    canvas.blit(gameOver_text_surface, gameOver_pos)

# def drawCat(): #not working yet
#     global canvas_width
#     canvas.blit(cat, (bird['x'], bird['y']))

def drawBackground():
  # canvas.fill(SKY_BLUE)
  global background_image 
  canvas.blit(background_image, (0, 0))

def drawBird():
  pygame.draw.rect(canvas, RED, (bird['x'], bird['y'], bird['width'], bird['height']))

# currentPipe is used to check what the previous option was to prevent the game from printing that option
currentPipe = 0
randHeight = 0

def addPipe():
  global last_pipe_x

# Randomly determine the height of the upper pipe and calculate the lower pipe's position
  upper_pipe_height = random.randint(100, 600)
  lower_pipe_height = canvas_height - upper_pipe_height - 175  # 150 is the gap between pipes

# Add the new upper and lower pipes
  new_top = {'x': canvas_width, 'y': 0, 'height': upper_pipe_height, 'width': pipe_width}
  new_bottom = {'x': canvas_width, 'y': canvas_height - lower_pipe_height, 'height': lower_pipe_height, 'width': pipe_width}
  pipe.append(new_top)
  pipe.append(new_bottom)

  last_pipe_x = canvas_width

def drawPipe():
  for p in pipe:
    pygame.draw.rect(canvas, BLACK, (p['x'], p['y'], pipe_width, p['height']))

def checkPipe():
  global last_pipe_x
  
  for p in pipe[:]:
    if p['x'] < -pipe_width:
      pipe.remove(p)
    else:
      last_pipe_x = p['x']

ground_height = 50  # Height of the ground
ground_color = GREEN  # Color of the ground

def drawGround():
# Draw the ground as a rectangle
  pygame.draw.rect(canvas, ground_color, (0, canvas_height - ground_height, canvas_width, ground_height))

def updateBird():
  a = 0

collide = False
def getCollision():
  print("Collision: ", collide)
  return collide

def collisionCheck():
  global pipe,bird,ground_height
  if not pipe:  # Check if pipe list is empty
        return False 
  p1 = pipe[0] #top pipe
  p2 = pipe[1] #bottom pipe

  if (bird['y'] + bird['height']) >= (canvas_height-ground_height): #ground collision
    #print("Bird Hit Ground")
    collide = True
    client_server.send_collision_to_server()
    client_server.collided = True
    return True 
  elif(bird['x'] + bird['width'] >= p2['x']) and (bird['x'] <= p2['x'] + 50) and ((bird['y'] + bird['height'] >= p2['y']) or ((bird['y'] <= p1['y'] + p1['height']))): #pipe collision
    #print("Bird Hit Wall")
    collide = True
    client_server.send_collision_to_server()
    client_server.collided = True
    return True
  return False

def pointCheck():
  global score, bird, pipe
  p2 = pipe[1] #bottom pipe

  if bird['x'] == p2['x'] + p2['width']:
    score += 1
    client_server.send_score_to_server(score)

def get_name():
  fontTitle = pygame.font.Font("pixelFont.ttf", 40) 
  font = pygame.font.Font(None, 36)
  input_box = pygame.Rect(180, 350, 190, 35)
  color = pygame.Color(255, 255, 255)
  text = ''
    
  while True:
    
    for event in pygame.event.get(): # detect events
      if event.type == pygame.QUIT:
        running = False
        pygame.quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          return text 
        elif event.key == pygame.K_BACKSPACE:
          text = text[:-1]
        else:
          text += event.unicode

      drawBackground()
      text_prompt = fontTitle.render("ENTER YOUR NAME:", True, (255, 255, 255))
      canvas.blit(text_prompt, (80, 280))
      txt_surface = font.render(text, True, color)
      canvas.blit(txt_surface, (185, 355))
      pygame.draw.rect(canvas, color, input_box, 2)

      pygame.display.flip()
      


def start(running, clock, frame_count, pipe_speed, birdgo, count, gamestart):
  global pipe, bird, acceleration, bird_mvt_delay, add_pipe_interval, collided
  while running and gamestart:
    dt = clock.tick(60) / 1000.0 # Limit to 60 frames per second and get time delta
    if collisionCheck() is True:
      
      client_server.collided = True 
      running = False
      player_score = score 
      
      if mode == "Singleplayer":
        # player_name = input("Enter your name: ")  # Get player name from terminal
        player_name = get_name() # Display on canvas
        leaderboard.save_score(player_name, player_score)
      elif mode == "Multiplayer":
        displayMatchResult.gameWinner(client_server.getResult())
        #while client_server.compareScores != "Done":
         # time.sleep(1)
        #print("Done")
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif (event.type == pygame.KEYDOWN) and (event.key == pygame.K_SPACE):
        birdgo = True
        bird['y'] += bird['jump']
        acceleration = 0

# bird_mvt_delay value is how many frames to delay the command by
        bird_mvt_delay = 7
      elif (event.type == pygame.KEYUP) and (event.key == pygame.K_s):
        running = False

    for p in pipe:
      p['x'] -= pipe_speed
    checkPipe()

# every 120 frames it adds a pipe
    frame_count += 1
    if frame_count >= add_pipe_interval:
      addPipe()
      frame_count = 0
# checks to see if the user pressed space to start already
# then added acceleration so that the bird falls better
    if birdgo is True:
      acceleration = acceleration + 50 * dt

# bird_mvt delay delays the next commands by the given amount of frames
      if bird_mvt_delay > 0:
        bird_mvt_delay = bird_mvt_delay - 1
      elif bird_mvt_delay <= 0:
        bird['y'] += (bird['gravity'] + acceleration * dt)
    
 
    drawBackground()
    drawBird()
    drawPipe()
    drawGround()
  
    pointCheck()
    scoreCountText()
    pygame.display.update()
    count += 1
  main.menu()
  pygame.quit()


gameStart = "Idle"
def drawTutorial():
  WHITE = (255,255,255)
  tutFont = pygame.font.Font("exitfont.ttf", 25) 
  tut_text_surface = tutFont.render("Press \"SPACE\" to jump!", True, WHITE)
  pos = (canvas_width // 2 - tut_text_surface.get_width() // 2, canvas_height - 100)
  canvas.blit(tut_text_surface, pos)
mode = ""
def game(gameType):
  global score, pipe, bird, acceleration, bird_mvt_delay, add_pipe_interval, mode
  mode = gameType
  print("Current Gamemode: ", mode)
  
  if mode == "Multiplayer":
    client_thread = threading.Thread(target=client_server.client_main)
    client_thread.start()
    while gameStart != "Start":
            c = ''
    print("Game Started")
  score = 0
  client_server.send_score_to_server(score)

# upper Pipe
  pipe = [
  {
    'x': pipeX,
    'y': y1,
    'color': (randint(0, 255), randint(0, 255), randint(0, 255)),
    'height': pipe_height,
    'width': pipe_width
  },
# lower Pipe
  {
    'x': pipeX,
    'y': y2,
    'color': (randint(0, 255), randint(0, 255), randint(0, 255)),
    'height': pipe_height,
    'width': pipe_width
  }
]
  running = True
  gamestart = False
# Checks for first input
  birdgo = False

# clock object to limit frame rate to prevent splitting (like Time delta in C# game engines for reference)
  clock = pygame.time.Clock()

  frame_count = 0

  bird['y'] = canvas_height // 2
  bird['velocityY'] = 0
  count = 0
  

  drawBackground()
  drawBird()
  drawGround()
  drawTutorial()
  pygame.display.update()

  while running:
    # print("score is", score)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
        pygame.quit()
      elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
        running = False
      else:
        gamestart = True
        pipe_speed = 0
        pipe_speed = 2.5
        birdgo = True
        bird['y'] += bird['jump']
        acceleration = 0
# bird_mvt_delay value is how many frames to delay the command by
        bird_mvt_delay = 7

        start(running, clock, frame_count, pipe_speed, birdgo, count, gamestart)

if __name__ == "__main__":
  game()
