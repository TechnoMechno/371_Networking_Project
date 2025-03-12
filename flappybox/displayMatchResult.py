import pygame 
import main
import client_server
import play
import server
pygame.init()

canvas_width = 600
canvas_height = 800
playCheck = True
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")
titleSize = 70
fontTitle = pygame.font.Font("pixelFont.ttf", titleSize) 
titlePosition = ((1/(titleSize/10))*canvas_width - 20, (1/4)*canvas_height) 
WHITE = (255,255,255)
result = "Loading..."

def drawMatchText(msg):
    if msg == "":
        result = "Loading..."
    else:
        result = msg
    text_surface = fontTitle.render(result, True, WHITE)
    canvas.blit(text_surface,titlePosition)

def gameWinner(msg):
    global playCheck, result

    
    while playCheck:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playCheck = False
                print("12123123")
            elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
                playCheck = False
                print("ajsdfaf")
                play.modes()
                print("starchio: ", msg)    
        if msg != "":
            # playCheck = False
            main.drawBackground()
            main.exitText()
            drawMatchText(msg)
            #print("msg ", msg)
            #print("playcheeck ", playCheck)
            pygame.display.update()
            try:
                client_server.client_socket.close()  # Close the client socket
                print("Client socket closed successfully")
            except Exception as e:
                print(f"Error closing client socket: {e}")
            server.stopServer()
            
    
    
if __name__ == "__main__":
  gameWinner()
