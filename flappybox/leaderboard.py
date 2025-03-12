import pygame 
import main
from pymongo import MongoClient
from pymongo import DESCENDING

pygame.init()

canvas_width = 600
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Flap Clam Game")
background_image = pygame.image.load("bg.png")

# Connect to the MongoDB client
try:
    client = MongoClient('localhost', 27017)
    db = client.flapClamGameDB
    leaderboard_collection = db.leaderboard
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


def save_score(player_name, player_score):
    leaderboard = {
        "player": player_name,
        "score": player_score
    }
    leaderboard_collection.insert_one(leaderboard)
    # print_all_scores()

def get_scores():
    all_scores = leaderboard_collection.find({}).sort("score", DESCENDING)
    # for score in all_scores:
    #     print(score)
    return list(all_scores)

def draw_high_scores(canvas, font, high_scores):
    startX, startY = 160, 200  # Starting position of the leaderboard on the canvas
    line_height = 30  # Height of each line

    fontTitle = pygame.font.Font("pixelFont.ttf", 50) 
    text_surface = fontTitle.render("Leaderboard", True, (255, 255, 255))
    canvas.blit(text_surface, (startX, 160)) #Set it a bit higher so it doesn't overlap with the rest of the text
    idx = 0

    for score in high_scores:
        if idx < 10:
            score_text = f"{idx + 1}) {score['player']}: {score['score']}"
            score_surface = font.render(score_text, True, (255, 255, 255))  # White color
            canvas.blit(score_surface, (startX, startY + (idx + 1) * line_height))
            idx += 1
        else:
            break


def drawBackground():
    global background_image 
    canvas.blit(background_image, (0, 0))


def board():
    top_10 = get_scores()
    font = pygame.font.Font(None, 40)
    
    execute = True
    
    while execute:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                execute = False
                pygame.quit() 
            elif (event.type == pygame.KEYUP) and (event.key == pygame.K_e):
                execute = False
        drawBackground()
        main.exitText()
        draw_high_scores(canvas, font, top_10)
        pygame.display.update()
                
    main.menu()

if __name__ == "__main__":
  board()
