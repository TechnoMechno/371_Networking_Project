# cookie.py
import pygame
import math
from config import *

class Cookie:
    # Class variable to track the currently dragged cookie
    currently_dragging = None
    
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
        self.on_plate = None
        self.original_position = list(position)  # Save starting position


    def handle_event(self, event, plates, players=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Only allow dragging if no other cookie is currently being dragged
            if Cookie.currently_dragging is None and self.rect.collidepoint(event.pos):
                if self.on_plate is not None:
                    self.on_plate = None
                self.dragging = True
                Cookie.currently_dragging = self
                self.offset[0] = event.pos[0] - self.position[0]
                self.offset[1] = event.pos[1] - self.position[1]
                self.original_position = self.position.copy()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                Cookie.currently_dragging = None
                # If not dropped on a plate, revert to original position
                if not self.check_plate_proximity(plates, players):
                    self.position = self.original_position.copy()
                    self.rect.center = self.position
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.position[0] = event.pos[0] - self.offset[0]
            self.position[1] = event.pos[1] - self.offset[1]
            self.rect.center = self.position

    def check_plate_proximity(self, plates, players=None):
        # Check proximity to all plates
        for i, plate in enumerate(plates):
            # Calculate distance from cookie center to plate center
            dx = self.position[0] - plate.x
            dy = self.position[1] - plate.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # If within the plate radius
            if distance < plate.radius:
                self.position[0] = plate.x
                self.position[1] = plate.y
                self.rect.center = self.position
                self.on_plate = plate
                
                # Award points if this is a player plate (assuming players list aligns with plates)
                if players is not None and i < len(players):
                    points = 2 if self.type == "star" else 1
                    players[i].score += points
                return True
        return False

    def is_on_central_plate(self, central_plate):   
        dx = self.position[0] - central_plate.x
        dy = self.position[1] - central_plate.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < central_plate.radius

    def draw(self, screen):
        screen.blit(self.image, self.rect)  # Draw the image at the rect position