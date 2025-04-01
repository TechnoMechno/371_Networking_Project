import pygame

class TextBox:
    def __init__(self, rect, text, font_name='Arial', font_size=24, 
                 bg_color=(0, 0, 0), text_color=(255, 255, 255), border_color=(255,255,255), border_width=2):
        """
        Initializes a text box.

        Parameters:
            rect (tuple or pygame.Rect): The area for the text box (x, y, width, height).
            text (str): The text to display.
            font_name (str): The name of the font to use.
            font_size (int): The size of the font.
            bg_color (tuple): The background color (RGB).
            text_color (tuple): The text color (RGB).
            border_color (tuple): The border color (RGB).
            border_width (int): The width of the border.
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.font = pygame.font.SysFont(font_name, font_size)

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        # Render the text
        text_surface = self.font.render(self.text, True, self.text_color)
        # Center text within the rect
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def set_text(self, new_text):
        """Update the text displayed in the text box."""
        self.text = new_text