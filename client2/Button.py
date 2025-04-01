import pygame

class Button:
    def __init__(self, rect, text, bg_color, text_color=(255, 255, 255), font_size=24):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', font_size)
        self.clicked = False

    def draw(self, screen):
        # Draw button rectangle
        pygame.draw.rect(screen, self.bg_color, self.rect)
        # Render and draw the text centered in the button.
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        # For example, return True if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f"Button.handle_event: event.pos = {event.pos}, button rect = {self.rect}")
            if self.is_clicked(event.pos):
                self.clicked = True
                return True
        return False