import pygame

class TextBox:
    def __init__(self, rect, text, font_name='Arial', font_size=24, 
                 bg_color=(220, 220, 220), text_color=(0, 0, 0), 
                 placeholder_color=(150, 150, 150), border_color=(0, 0, 0), border_width=2):
        """
        Initializes a text box.
        """
        self.rect = pygame.Rect(rect)
        self.text = ""  # User-entered text
        self.default_text = text  # Placeholder text
        self.bg_color = bg_color
        self.text_color = text_color
        self.placeholder_color = placeholder_color  # Faded color for default text
        self.border_color = border_color
        self.border_width = border_width
        self.font = pygame.font.SysFont(font_name, font_size)
        self.active = False  # Whether this box is currently active

    def draw(self, screen, blink=False):
        # Draw background and border
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Choose which text and color to display:
        if self.text:
            display_text = self.text
            display_color = self.text_color
        else:
            display_text = self.default_text
            display_color = self.placeholder_color

        # Add blinking cursor if active.
        if self.active and blink:
            display_text += "|"
            
        text_surface = self.font.render(display_text, True, display_color)
        # Left-align with a little padding; adjust as needed.
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)

    def add_char(self, char):
        self.text += char

    def remove_char(self):
        self.text = self.text[:-1]

    def set_active(self, active):
        self.active = active

    def get_text(self):
        return self.text
