import pygame 
import main
import play
pygame.init()

canvas_width = 600
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")
titleSize = 70
fontTitle = pygame.font.Font("pixelFont.ttf", titleSize) 
titlePosition = ((1/(titleSize/10))*canvas_width - 20, (1/4)*canvas_height) 
titleBelowPosition = ((1/(titleSize/10))*canvas_width - 20, (1/4)*canvas_height+75) 

WHITE = (255,255,255)

def drawMatchText():
    text_surface = fontTitle.render("  Waiting for", True, WHITE)
    text_below = fontTitle.render("players to join...", True, WHITE)

    canvas.blit(text_surface,titlePosition)
    canvas.blit(text_below,titleBelowPosition)

def loading():
    #clients Connected = true means that their not connected, when its changed to false 2 clients have been connected
    clientsConnected = True
    while clientsConnected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                clientsConnected = False
            elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
                play.modes()
        main.drawBackground()
        main.exitText()
        drawMatchText()
        pygame.display.update()
   
        

if __name__ == "__main__":
  loading()
