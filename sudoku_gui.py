from sudoku import Sudoku
from sudoku_gui_board import Board
from random import randint
from labels import StrikesLabel, Label
from button import Button
import pygame
import threading

_FRAME_RATE = 60
_INITIAL_HEIGHT = 756
_INITIAL_WIDTH = 1200


class SudokuGUI:
    """Represents a GUI that allows the user to play Sudoku."""

    def __init__(self) -> None:
        """Initializes the state of the GUI."""
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", 27, True)
        self._game_state = Sudoku()
        self._board = Board(self._game_state, font)
        self._running = True
        self._set_up_labels(font)
        self._set_up_buttons(font)
        self._touch_active = False

    def _set_up_labels(self, font) -> None:
        """Sets up the labels for the game."""
        self._strikes_label = StrikesLabel(830, 50, 230, 50, '', font, 3, (255, 255, 255))
        self._strikes_label.set_text_position(1, 1)
        self._label = Label(830, 670, 300, 80, '', font, 3, (200, 200, 100))
        self._label.set_text_position(7, 3)

    def _set_up_buttons(self, font) -> None:
        """Sets up the button for the game."""
        scrape_easy_puzzle = (lambda: self._game_state.webscrape_puzzle(('easy', randint(1, 3))))
        scrape_medium_puzzle = (lambda: self._game_state.webscrape_puzzle(('medium', randint(4, 6))))
        scrape_hard_puzzle = (lambda: self._game_state.webscrape_puzzle(('hard', randint(7, 9))))

        self._solve_button = Button(830, 150, 150, 70, self._game_state.solve,
                                    (45, 117, 114), (52, 235, 229), 'Solve', font, 3)

        self._generate_button = Button(830, 250, 150, 70, self._game_state.generate_puzzle,
                                       (122, 23, 108), (235, 14, 205), "Create", font, 3)

        self._easy_button = Button(1000, 150, 150, 70, scrape_easy_puzzle,
                                   (34, 97, 9), (119, 250, 67), 'Easy', font, 3)

        self._medium_button = Button(1000, 250, 150, 70, scrape_medium_puzzle,
                                     (138, 47, 94), (255, 122, 191), 'Medium', font, 3)

        self._hard_button = Button(1000, 350, 150, 70, scrape_hard_puzzle,
                                   (138, 6, 6), (255, 77, 77), "Hard", font, 3)

        self._solve_button.set_text_position(5, 3)
        self._generate_button.set_text_position(6, 3)
        self._easy_button.set_text_position(5, 3)
        self._medium_button.set_text_position(9, 3)
        self._hard_button.set_text_position(5, 3)

    def _set_states(self) -> None:
        if self._game_state.is_generating or self._game_state.is_solving:
            self._solve_button.active = False
            self._generate_button.active = False
            self._easy_button.active = False
            self._medium_button.active = False
            self._hard_button.active = False
            self._board.is_clickable = False
            self._touch_active = False
        else:
            self._board.is_clickable = True
            self._solve_button.active = True
            self._generate_button.active = True
            self._easy_button.active = True
            self._medium_button.active = True
            self._hard_button.active = True

    def _is_completed(self) -> bool:
        """Returns True if the user solved the board himself."""
        if self._game_state.zeros is not None:
            return len(self._board.user_moves) == self._game_state.zeros
        return False

    def run_game(self) -> None:
        """Runs the game."""
        try:
            pygame.init()
            pygame.display.set_caption("SUDOKU")
            clock = pygame.time.Clock()
            pygame.display.set_mode((_INITIAL_WIDTH, _INITIAL_HEIGHT))
            while self._running:
                clock.tick(_FRAME_RATE)
                self._set_states()                
                self._handle_events()
                self._strikes_label.strikes = self._board.strikes % (3 + 1)
                self._redraw()
        finally:
            pygame.quit()

    def _handle_events(self) -> None:
        """Handles all the events that occur during the game."""
        mouse_position = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._end_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_clicks(mouse_position)
            if event.type == pygame.KEYDOWN:
                self._handle_key_presses(event.key)
            self._handle_button_commands(mouse_position)
        if self._board.strikes == 3:
            self._game_state.solve()
            self._label.text = "YOU LOST!"
        if self._game_state.is_full() and self._is_completed():
            self._label.text = 'YOU WON!'

    def _handle_button_commands(self, position: (int, int)) -> None:
        """Handles all the button commands."""
        self._solve_button.is_mouse_on_button(position)
        self._generate_button.is_mouse_on_button(position)
        self._easy_button.is_mouse_on_button(position)
        self._medium_button.is_mouse_on_button(position)
        self._hard_button.is_mouse_on_button(position)

    def _handle_key_presses(self, event) -> None:
        """Handles all the key presses."""
        if event == pygame.K_ESCAPE:
            self._end_game()
        elif event == pygame.K_1:
            self._board.input_move(1)
        elif event == pygame.K_2:
            self._board.input_move(2)
        elif event == pygame.K_3:
            self._board.input_move(3)
        elif event == pygame.K_4:
            self._board.input_move(4)
        elif event == pygame.K_5:
            self._board.input_move(5)
        elif event == pygame.K_6:
            self._board.input_move(6)
        elif event == pygame.K_7:
            self._board.input_move(7)
        elif event == pygame.K_8:
            self._board.input_move(8)
        elif event == pygame.K_9:
            self._board.input_move(9)
        elif event == pygame.K_RETURN:
            self._board.enter_entry()
        elif event == pygame.K_BACKSPACE:
            self._board.delete_entry()
        elif not self._game_state.is_full():
            print('click breaks this board')
            if self._touch_active and event == pygame.K_UP:
                self._board.change_direction(-1, 0)
            elif self._touch_active and event == pygame.K_DOWN:
                self._board.change_direction(1, 0)
            elif self._touch_active and event == pygame.K_LEFT:
                self._board.change_direction(0, -1)
            elif self._touch_active and event == pygame.K_RIGHT:
                self._board.change_direction(0, 1)

    def _handle_mouse_clicks(self, position: (int, int)) -> None:
        """Handles all the mouse click events."""
        if self._board.is_board_clicked(position):
            col, row = position
            cell_width, cell_height = self._board.cell_size
            self._board.selected_cell = (row // cell_width, col // cell_height)
        if self._solve_button.is_mouse_on_button(position):
            solve = threading.Thread(target=self._solve_button.execute)
            solve.start()
        if self._generate_button.is_mouse_on_button(position):
            generate = threading.Thread(target=self._generate_button.execute)
            generate.start()
            self._set_game()
        if self._easy_button.is_mouse_on_button(position):
            generate = threading.Thread(target=self._easy_button.execute)
            generate.start()
            self._set_game()
        if self._medium_button.is_mouse_on_button(position):
            generate = threading.Thread(target=self._medium_button.execute)
            generate.start()
            self._set_game()
        if self._hard_button.is_mouse_on_button(position):
            generate = threading.Thread(target=self._hard_button.execute)
            generate.start()
            self._set_game()

    def _set_game(self) -> None:
        """Sets up the basic requirements in order for the user to play."""
        self._board.strikes = 0
        self._board.clear_moves()
        self._board.selected_cell = (None, None)
        self._label.text = ''
        self._touch_active = True

    def _end_game(self) -> None:
        """Ends the game."""
        self._running = False

    def _redraw(self) -> None:
        """Draws the current state of the GUI."""
        surface = pygame.display.get_surface()
        self._board.update_game(self._game_state)
        self._board.set_board_dimensions(surface)
        background_color = (161, 255, 181)
        surface.fill(background_color)
        self._board.draw_board()
        self._strikes_label.draw_display(surface)
        self._solve_button.draw_button(surface)
        self._generate_button.draw_button(surface)
        self._easy_button.draw_button(surface)
        self._medium_button.draw_button(surface)
        self._hard_button.draw_button(surface)
        self._label.draw_display(surface)
        pygame.display.flip()


if __name__ == '__main__':
    game = SudokuGUI()
    game.run_game()
