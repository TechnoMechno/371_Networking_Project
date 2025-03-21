# cookie.py
import pygame
from config import *

class Cookie:
    def __init__(self, position, type="regular"):
        self.position = list(position)
        self.type = type
        try:
            image_path = REGULAR_COOKIE_IMAGE if self.type == "regular" else STAR_COOKIE_IMAGE
            self.image = pygame.image.load(image_path).convert_alpha()
            # Scale the image to COOKIE_SIZE
            self.image = pygame.transform.smoothscale(self.image, (COOKIE_SIZE, COOKIE_SIZE))
        except pygame.error as e:
            print(f"Error loading image: {e}")
            pygame.quit()
            exit()
        self.rect = self.image.get_rect(center=position)
        self.dragging = False
        self.offset = [0, 0]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.offset[0] = event.pos[0] - self.position[0]
                self.offset[1] = event.pos[1] - self.position[1]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.position[0] = event.pos[0] - self.offset[0]
            self.position[1] = event.pos[1] - self.offset[1]
            self.rect.center = self.position
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)  # Draw the image at the rect position