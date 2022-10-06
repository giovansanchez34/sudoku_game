import pygame

class Label:
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font, boarder_width: int, color: (int,)) -> None:
        """Initializes the state of the label."""
        self._coordinates = (x, y)
        self._set_dimensions(width, height)
        self._font = font
        self._text = text
        self._color = color
        self._boarder_width = boarder_width
    
    @property
    def text(self) -> str:
        """Returns the text that is displayed on the label."""
        return self._text
    
    @text.setter
    def text(self, new_text: str) -> None:
        """
        Sets the new text to the text that would be
        displayed on the label.
        """
        self._text = new_text
        
    
    @property
    def coordinates(self) -> (int, int):
        """Returns the (x,y) coordinate of the label."""
        return self._coordinates
    
    def _set_dimensions(self, width: int, height: int) -> None:
        """Sets the dimensions of the display label."""
        self._width = width # 250
        self._height = height # 50
        x, y = self.coordinates
        self._rect = (x, y, self._width, self._height)
    
    def set_text_position(self, x_div: int, y_div: int) -> None:
        """Sets the coordinate of the text."""
        x, y, width, height = self._rect
        self._text_position = (x + width // x_div, y + height // y_div, 20, 20)
        
    def draw_display(self, surface: pygame.surface) -> None:
        """Draws the display label onto the surface."""
        #white = (255, 255,255)
        black = (0, 0, 0)
        pygame.draw.rect(surface, self._color, self._rect)
        #pygame.draw.rect(surface, white, self._rect)
        pygame.draw.rect(surface, black, self._rect, self._boarder_width)
        self._display_text(surface)
        
    def _display_text(self, surface: pygame.surface) -> None:
        """Displays the text on the label."""
        black = (0, 0, 0)
        text_font = self._font.render(str(self._text), True, black)
        surface.blit(text_font, self._text_position)
    

class StrikesLabel(Label):
    """
    Represents a special type of label that is able
    to display how many times the user entered a wrong entry.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font, boarder_width: int, color: (int,)) -> None:
        """Initializes the state of the display board."""
        Label.__init__(self, x, y, width, height, '', font, boarder_width, color)
        self.strikes = 0
    
    def draw_display(self, surface: pygame.surface) -> None:
        """Draws the display label."""
        Label.draw_display(self, surface)
        self._draw_strikes(surface)
        self._draw_lines(surface)
        
    def _draw_lines(self, surface: pygame.surface) -> None:
        """Draw lines on the display board to separate the X's."""
        x,y = self.coordinates
        black = (0, 0, 0)
        start_x, start_y = x, y
        end_x, end_y = x , y + self._height
        for _ in range(3-1):
            start_x += self._width // 3
            end_x += self._width // 3
            pygame.draw.line(surface, black, (start_x, start_y), (end_x, end_y),4)
            
    
    def _draw_strikes(self, surface: pygame.surface) -> None:
        """Draws X's for the number of strikes the user."""
        x, y = self.coordinates
        red = (148, 7, 7)
        start_x, start_y = x + 10, y
        end_x, end_y = x + 75, y + 200
        for _ in range(self.strikes):
            text = self._font.render("X", True, red)
            surface.blit(text,(start_x, start_y, end_x, end_y) )
            start_x += 100
            end_x = start_x + 75
            
    @property
    def strikes(self) -> int:
        """Returns the value of tracks."""
        return self._strikes
    
    @strikes.setter
    def strikes(self, value) -> None:
        """Sets the new value to tracks."""
        self._strikes = value





    