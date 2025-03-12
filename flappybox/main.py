import pygame
import game
import play

#NOTE PLEASE DO NOT START BOTH MULTIPLAYER CLIENTS AT THE SAME TIME WAIT TILL SERVER IS UP THEN START the other multiplayer client!

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

#Ground
ground_height = 50  # Height of the ground
ground_color = GREEN  # Color of the ground

# Set up for text (title)
titleSize = 70
fontTitle = pygame.font.Font("pixelFont.ttf", titleSize) 
titlePosition = ((1/(titleSize/10))*canvas_width - 20, (1/4)*canvas_height) #idk how to put it in the middle

def drawBackground():
    global background_image 
    canvas.blit(background_image, (0, 0))
    
def drawBird():
    pygame.draw.rect(canvas, RED, (game.bird['x'], game.bird['y'], game.bird['width'], game.bird['height']))

def drawGround():
# Draw the ground as a rectangle
    pygame.draw.rect(canvas, ground_color, (0, canvas_height - ground_height, canvas_width, ground_height))

#add title text
def titleText():
    text_surface = fontTitle.render("FLAP CLAM!", True, WHITE)
    canvas.blit(text_surface,titlePosition)

#add instruction text - exit
def exitText():
    exitFont = pygame.font.Font("exitfont.ttf", 25) 
    exit_text_surface = exitFont.render("Press e to esc", True, WHITE)
    pos = (canvas_width // 2 - exit_text_surface.get_width() // 2, canvas_height - 100)
    canvas.blit(exit_text_surface, pos)


#button MAKE LOOK NICER
font = pygame.font.Font(None, 36)
button_width = 200
button_height = 50

#start button
play_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2, button_width, button_height)
play_button_text = font.render("PLAY", True, BLACK)
play_text_position = ((play_button_rect.left + play_button_rect.right - play_button_text.get_width()) // 2, (play_button_rect.top + play_button_rect.bottom - play_button_text.get_height()) // 2)



# exit button
exit_button_rect = pygame.Rect((canvas_width - button_width) // 2, (canvas_height - button_height) // 2 + button_height + 20, button_width, button_height)
exit_button_text = font.render("EXIT", True, BLACK)
exit_text_position = ((exit_button_rect.left + exit_button_rect.right - exit_button_text.get_width()) // 2, (exit_button_rect.top + exit_button_rect.bottom - exit_button_text.get_height()) // 2)

def drawButton(rect, button_text, text_position):
    pygame.draw.rect(canvas, WHITE, rect)
    canvas.blit(button_text, text_position)

#point refers to position of cursor
#rect.left and etc is used to check if the cursor is in the rect
def clicked(point, rect):
    return (rect.left <= point[0] <= rect.right) and (rect.top <= point[1] <= rect.bottom)

def menu():
    global bird
    execute = True
    
    while execute:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                execute = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if clicked(event.pos, play_button_rect):
                    play.modes()
              
                elif clicked(event.pos, exit_button_rect):
                    execute = False
        drawBackground()
        titleText()
        #exitText()
        drawBird()
        drawGround()

        #buttons
        drawButton(play_button_rect, play_button_text, play_text_position)
        drawButton(exit_button_rect, exit_button_text, exit_text_position)

        pygame.display.update()
        

    pygame.quit()

if __name__ == "__main__":
  menu()
