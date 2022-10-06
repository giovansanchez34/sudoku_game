import pygame


class Board:
    """Represents the interactive sudoku board."""

    def __init__(self, sudoku: 'Sudoku', font) -> None:
        """Initializes the state of the sudoku board."""
        self._selected_cell = (None, None)
        self._game = sudoku
        self._user_moves = {}
        self.strikes = 0  # number of times user has entered a wrong input
        self._font = font
        self.is_clickable = False

    @property
    def is_clickable(self) -> bool:
        """Returns the state of the board."""
        return self._is_clickable

    @is_clickable.setter
    def is_clickable(self, state: bool) -> None:
        """Sets up the state of the board."""
        self._is_clickable = state

    @property
    def user_moves(self) -> {(int, int): int}:
        """Returns user_moves attribute."""
        return self._user_moves

    def clear_moves(self) -> None:
        """Clears user moves."""
        self._user_moves.clear()

    def update_game(self, sudoku: 'Sudoku') -> None:
        """Updates the state of the game."""
        self._game = sudoku

    @property
    def strikes(self) -> int:
        """Returns the number of times a user can get wrong."""
        return self._strikes

    @strikes.setter
    def strikes(self, value: int) -> None:
        """Sets the strikes attribute to the new value."""
        self._strikes = value

    @property
    def selected_cell(self) -> (int, int):
        """Returns the position of the selected cell."""
        return self._selected_cell

    @selected_cell.setter
    def selected_cell(self, position: (int, int)) -> None:
        """Sets selected cell to the new position."""
        self._selected_cell = position

    def change_direction(self, dx: int, dy: int) -> None:
        if self.selected_cell == (None, None):
            self.selected_cell = min(self._game.pencil_marks, default=(None, None))
        else:
            x, y = self.selected_cell
            while True:
                new_coord = ((x + dx) % 9, (y + dy) % 9)
                if new_coord in self._game.pencil_marks:
                    break
                x += dx
                y += dy
            self.selected_cell = new_coord

    @property
    def cell_size(self) -> (int, int):
        """Returns the width and height of the cell."""
        return self._cell_width, self._cell_height

    def set_board_dimensions(self, surface: pygame.surface) -> None:
        """
        Sets the dimensions of the sudoku board.
        """
        self._surface = surface
        self._x, self._y = 0, 0
        difference = self._surface.get_width() - self._surface.get_height()
        self._width = self._surface.get_width() - difference
        self._height = self._surface.get_height()
        self._dimension = pygame.Rect((self._x, self._y, self._width, self._height))
        self.cell_size = (self._width, self._height)

    @cell_size.setter
    def cell_size(self, dimension: (int, int)) -> None:
        """Sets the size of each cell in the board."""
        width, height = dimension
        self._cell_width = width // 9
        self._cell_height = height // 9

    def draw_board(self) -> None:
        """Draws the sudoku game board onto the pygame window."""
        pygame.draw.rect(self._surface, (255, 255, 255), self._dimension)
        self._draw_selected_cell()
        self._draw_clues()
        self._draw_rows()
        self._draw_columns()

    def _draw_rows(self) -> None:
        """Draws the rows of the board."""
        x, y = self._x, self._y
        for row in range(1, 10):
            y += self._cell_width
            line_width = 3 if row % 3 == 0 else 1
            start_point = (x, y)
            end_point = (self._width, y)
            self._draw_line(start_point, end_point, line_width)

    def _draw_line(self, start: (int, int), end: (int, int), width: int) -> None:
        """Draws the line at the given coordinate."""
        black = (0, 0, 0)
        pygame.draw.line(self._surface, black, start, end, width)

    def _draw_columns(self) -> None:
        """Draws the columns of the board."""
        x, y = self._x, self._y
        for col in range(1, 10):
            x += self._cell_height
            line_width = 3 if col % 3 == 0 else 1
            start_point = (x, y)
            end_point = (x, self._height)
            self._draw_line(start_point, end_point, line_width)

    def _draw_selected_cell(self):
        """
        Highlights the selected cell to indicate to the user which cell he
        is interacting with. 
        """
        self.selected_cell = self.selected_cell if self.is_clickable else (None, None)
        x, y = self.selected_cell
        if self.selected_cell in self._game.pencil_marks:
            light_blue = (48, 238, 255)
            cell_width, cell_height = self.cell_size
            pygame.draw.rect(self._surface, light_blue, (y * cell_width, x * cell_height, cell_width, cell_height))

    def input_move(self, entry: int) -> None:
        """Inputs the number onto the board's surface."""
        if self.selected_cell in self._game.pencil_marks:
            self._user_moves[self._selected_cell] = entry

    def _draw_clues(self) -> None:
        """Draws all the clues onto the board's surface."""
        x, y = self._x, self._y
        cell_width, cell_height = self.cell_size
        y_point = (y + cell_height) // 3 + 3
        for row_pos, row in enumerate(self._game.board):
            x_point = (x + cell_width) // 3 + 3
            for col_pos, entry in enumerate(row):
                position = (x_point, y_point, cell_width // 3, cell_height // 3)
                if (row_pos, col_pos) not in self._game.pencil_marks and entry != 0:
                    self._fill_locked_cell((row_pos, col_pos))
                    self._display_clue(entry, position)
                elif (row_pos, col_pos) in self._user_moves:
                    entry = self._user_moves[(row_pos, col_pos)]
                    self._display_clue(entry, position, (156, 156, 156))
                x_point += cell_width
            y_point += cell_height

    def delete_entry(self) -> None:
        """Deletes the entry that the user entered on the selected cell."""
        if self.selected_cell in self._game.pencil_marks \
                and self.selected_cell in self._user_moves:
            self._user_moves.pop(self.selected_cell)

    def enter_entry(self) -> None:
        """Enters the entry that the user entered on the selected cell."""
        entry = self._user_moves.get(self.selected_cell, None)
        if entry and not self._game.valid_move(self.selected_cell, entry):
            self.strikes += 1

    def _fill_locked_cell(self, position: (int, int)) -> None:
        """
        These cells are filled in grey to indicate that these clues 
        were already present since the beginning of the game.
        """
        x, y = position
        cell_width, cell_height = self.cell_size
        pygame.draw.rect(self._surface, (180, 180, 180), ((y * cell_width), (x * cell_height), cell_width, cell_height))

    def _display_clue(self, clue: int, position: (int, int), color: (int,) = None) -> None:
        """Draws the available clue onto the board."""
        clue = '' if self._game.is_generating else clue
        color = (0, 0, 0) if color is None else color
        text = self._font.render(str(clue), True, color)
        self._surface.blit(text, position)

    def is_board_clicked(self, position: (int, int)) -> bool:
        """Returns True if the board was clicked on."""
        return self._dimension.collidepoint(position)
