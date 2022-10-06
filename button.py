import pygame



class Button:
    """Represents a clickable button."""
    
    def __init__(self, x: int, y: int, width: int, height: int, command: callable, color: (int,), hover_color: (int,), text: str, font, boarder_width: int, active: bool = True) -> None:
        """Initializes the state of the button."""
        self._dimension = (x, y, width, height)
        self._button = pygame.Rect(self._dimension)
        self._idle_color = color
        self._button_color = color
        self._hover_color = hover_color
        self._text = text
        self._command = command
        self._font = font
        self._boarder_width = boarder_width
        self.active = active
    
    @property
    def active(self) -> bool:
        """Returns the state of the button."""
        return self._active
    @active.setter
    def active(self, state: bool) -> None:
        """Sets the state of the button."""
        self._active = state        
        
    def set_text_position(self, x_div: int, y_div: int) -> None:
        """Sets the coordinate of the text."""
        x, y, button_width, button_height = self._dimension
        self._text_position = (x + button_width // x_div, y + button_height // y_div, 20, 20)
       
    
    def draw_button(self, surface: pygame.surface):
        pygame.draw.rect(surface, self._button_color, self._button,)
        pygame.draw.rect(surface, (0, 0, 0), self._button, self._boarder_width)
        self._display_text(surface)
    
    def _display_text(self, surface: pygame.surface) -> None:
        """Displays the text on the surface of the button."""
        black = (0, 0, 0)
        text = self._font.render(str(self._text), True, black)
        surface.blit(text, self._text_position)
    
    def execute(self) -> None:
        """
        Executes the given command function when the button is clicked and active.
        """
        if self.active:
            self._command()
        
        
    
    def is_mouse_on_button(self, position: (int, int)) -> bool:
        """Returns True if the mouse is on the button."""
        
        is_on_button = self._button.collidepoint(position)
        self._button_color = self._hover_color if is_on_button else self._idle_color
        return is_on_button
    
            