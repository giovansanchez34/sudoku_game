from itertools import product
from math import sqrt
from random import shuffle, randint
from copy import deepcopy
from sudoku_scraper import get_sudoku_puzzle, get_sudoku_solution


class Sudoku:
    
    def __init__(self) -> None:
        """Initializes the state of the Sudoku Game."""
        self._rows = 9
        self._columns = 9
        self._board = [[0 for _ in range(self._columns)] for _ in range(self._rows)]
        self._counter = 0
        self._solution = [[0 for _ in range(self._columns)] for _ in range(self._rows)]
        self._history = {}
        self._zeros = None
        self.is_generating = False
        self.is_solving = False
        
    @property
    def is_generating(self) -> bool:
        return self._is_generating
    
    @is_generating.setter
    def is_generating(self, state: bool) -> None:
        self._is_generating = state
    
    @property
    def is_solving(self) -> bool:
        return self._is_solving 
    
    @is_solving.setter
    def is_solving(self, state: bool) -> None:
        self._is_solving = state
        
    @property
    def zeros(self) -> int:
        """Returns the number of clues available on the board."""
        return self._zeros
    
    @property
    def board(self) -> [[int]]:
        """Returns the NxN sudoku board."""
        return self._board
    
    @property
    def pencil_marks(self) -> {(int, int): {int}}:
        """
        Returns that history dictionary that contains all the coordinates of
        the empty cells and their possible values.
        """
        return self._history

    def _new_game(self) -> None:
        """Resets the board."""
        for row in range(self._columns):
            for col in range(self._rows):
                self.board[row][col] = 0
    
    def valid_move(self, coord: (int, int), entry: int) -> bool:
        """
        Returns True if the entry can be entered at the given
        coordinate.
        """
        row, col = coord
        if self._solution[row][col] == entry:
            self.pencil_marks.pop(coord)
            self.board[row][col] = entry
            return True
        return False

    def find_blank_cell(self) -> (int, int):
        """
        Finds/returns the first coordinate of an empty cell it finds
        in the board.
        """
        for row_pos, row in enumerate(self.board):
            for col_pos, entry in enumerate(row):
                if entry == 0:
                    return row_pos, col_pos

    def _generate(self) -> bool:
        """
        Recursively creates a sudoku puzzle using backtracking algorithm.
        """
        coord = self.find_blank_cell()
        if not coord:
            return True
        else:
            row, col = coord
            numbers = list(range(1, self._columns + 1))
            shuffle(numbers)
            for number in numbers:
                if self.is_valid_entry(number, (row, col)):
                    self.board[row][col] = number
                    if self._generate():
                        return True
                    self.board[row][col] = 0
            return False

    def generate_puzzle(self) -> None:
        """
        Generates a completed sudoku puzzle that follows the rules
        of a valid sudoku puzzle.
        """
        self._new_game()
        self.is_generating = True
        self.pencil_marks.clear()
        self._generate()
        self._shuffle_sudoku_board()
        self._create_puzzle()
        self._zeros = len(self.pencil_marks)
        self.is_generating = False
        
    def _shuffle_sudoku_board(self) -> None:
        """
        Shuffles the sudoku board to randomize the values while maintaining
        the integrity of the board.
        """
        count = 0
        for row1, row2 in Sudoku._generate_number():
            count += 1
            self.board[row1], self.board[row2] = self.board[row2], self.board[row1]
            if count % 6 == 0:
                break
        
        for col1, col2 in Sudoku._generate_number():
            count += 1
            for row in range(self._rows):
                self.board[row][col1], self.board[row][col2] = self.board[row][col2], self.board[row][col1]
            if count % 6 == 0:
                break

    @staticmethod
    def _generate_number() -> (int, int):
        lower_limit = 0
        while True:
            pos1 = randint(lower_limit % 9, (lower_limit % 9) + 2)
            pos2 = randint(lower_limit % 9, (lower_limit % 9) + 2)
            if pos1 != pos2:
                yield pos1, pos2
                lower_limit += 3

    def webscrape_puzzle(self, response: (str, str)) -> None:
        self.pencil_marks.clear()
        puzzle_id = get_sudoku_puzzle(response, self._board)
        get_sudoku_solution(('solution', int(puzzle_id)), self._solution)
        self._create_pencil_marks()
        self._zeros = len(self.pencil_marks)

    def print_puzzle(self):
        """Prints a neatly formatted sudoku grid."""
        mod = int(sqrt(self._rows))
        power = self._rows * mod
        for j, row in enumerate(self.board, start=1):
            for i, entry in enumerate(row, start=1):
                print(' ' if entry == 0 else entry, end=' ')
                print('|' if i % mod == 0 and i != self._rows else '', end=' ')
            print('\n' + '-' * power if j % mod == 0 and j != self._rows else '')

    def is_full(self) -> bool:
        """Board is solved if every spot is filled with a number."""
        return all(0 not in row for row in self.board)

    def is_correct_solution(self) -> bool:
        """
        Returns True if the solved puzzle is valid by checking all its rows
        columns and blocks.
        """
        return all(self.is_valid_entry(entry, (i, j))
                   for i, row in enumerate(self.board) for j, entry in enumerate(row))

    def is_valid_entry(self, entry, coord: (int, int)) -> bool:
        """
        Returns True if the given entry at the given coord is correct
        by checking if it is not in row, column, and its box.
        """
        if not self._is_valid_block_entry(entry, coord):
            return False
        elif not self._is_valid_row_entry(entry, coord):
            return False
        elif not self._is_valid_col_entry(entry, coord):
            return False
        return True
        
    def _is_valid_row_entry(self, entry: int, coord: (int, int)) -> bool:
        """Returns True if entry is not in the row."""
        x, y = coord
        return all(entry != number for i, number in enumerate(self.board[x]) if y != i)
    
    def _is_valid_col_entry(self, entry: int, coord: (int, int)) -> bool:
        """Returns True if entry is not in the column."""
        x, y = coord
        return all(entry != self.board[i][y] for i, _ in enumerate(self.board) if i != x)
    
    def determine_block(self, coord: (int, int)):
        """
        Determines/Returns a generator of coordinates that reside in the same
        block that the given coordinates belongs to.
        """
        row, col = coord
        mod = int(sqrt(self._columns))
        row_range = range(row + -(row % mod), row + abs(row % mod - mod))
        col_range = range(col + -(col % mod), col + abs(col % mod - mod))
        return product(row_range, col_range)

    def _is_valid_block_entry(self, entry: int, coord: (int, int)) -> bool:
        """Returns True if entry is not in the 3 x 3 block."""
        block = self.determine_block(coord)
        return all(entry != self.board[row][col] for row, col in block if coord != (row, col))

    def _create_puzzle(self):
        """
        Carefully determines which cells should be removed from the filled sudoku board to
        create the puzzle while ensuring that the algorithm maintains the same solution.
        """
        cells = list(product(range(self._rows), range(self._rows)))
        rounds = 30
        self._solution = deepcopy(self.board)
        
        while rounds and len(self.pencil_marks) <= 61:
            shuffle(cells)
            row, col = cells.pop()
            entry = self.board[row][col]
            
            self.board[row][col] = 0
            self._create_pencil_marks()
            self._counter = 0
            self._solve_puzzle('remove')
            
            if self._counter != 1:
                rounds -= 1
                self.board[row][col] = entry
                self.pencil_marks.pop((row, col))
                cells.append((row, col))
        self._create_pencil_marks()
    
    def solve(self) -> None:
        self.is_solving = True
        self._solve_puzzle()
        self.is_solving = False

    def _solve_puzzle(self, action: str = 'solve') -> bool:
        """
        If the given action is 'solve', the function solves the current sudoku
        puzzle using the backtracking algorithm in addition with least constraining value
        heuristic, most constrained heuristic, and forward checking.
        If the given action is 'remove', the function carefully picks which cells
        should be empty while ensuring the solution has a unique solution.
        It also uses the same algorithm.
        """
        coord = min(self.pencil_marks, default='empty', key=lambda coord: len(self.pencil_marks[coord]))
        if coord == 'empty':
            return True 
        else:
            row, col = coord
            possible_entries = self.pencil_marks[coord]
            failed_entries = set()
            self.pencil_marks.pop(coord)
            while possible_entries:
                number = self._least_constraining_value(coord, possible_entries)
                possible_entries.discard(number)
                if self.is_valid_entry(number, coord):
                    self.board[row][col] = number
                    self._forward_checking(coord, number, 'discard')
                    if self._solve_puzzle(action):
                        if action == 'remove':
                            self._counter += 1
                        else:
                            return True
                    self._forward_checking(coord, number, 'add')
                    self.board[row][col] = 0
                    failed_entries.add(number)
            if action == 'remove':
                self.board[row][col] = 0
            self.pencil_marks[coord] = failed_entries
            return False

    def _least_constraining_value(self, coord: (int, int), entries: [int]) -> int:
        """
        Following the least constraining value heuristic, this function
        returns the entry from the given entry list that least appears in its
        row, column, and block.
        """
        neighboring_values = self._find_neighboring_values(coord)
        values = [*entries]
        for value in neighboring_values:
            values.extend(self.pencil_marks[value])
        return min(entries, key=lambda value: values.count(value))
                    
    def _find_neighboring_values(self, coord: (int, int)) -> {(int, int)}:
        """
        Returns a set of coordinates that are in the same row, column and 
        block as the given coordinate.
        """
        row, col = coord
        block = self.determine_block(coord)
        row_values = {(row, pos) for pos in range(self._rows) if (row, pos) in self.pencil_marks}
        col_values = {(pos, col) for pos in range(self._columns) if (pos, col) in self.pencil_marks}
        block_values = {pos for pos in block if pos in self.pencil_marks}
        neighboring_values = set()
        neighboring_values.update(row_values, col_values, block_values)
        return neighboring_values
    
    def _create_pencil_marks(self) -> None:
        """
        Creates a dictionary that contains the coordinates of cells that 
        are empty and the possible values that can go into each cell.
        """
        clues_coords = []
        for row_pos, row in enumerate(self.board):
            for col_pos, entry in enumerate(row):
                if entry == 0:
                    self.pencil_marks[(row_pos, col_pos)] = set(range(1, self._rows + 1))
                else:
                    clues_coords.append((row_pos, col_pos, entry))
        for row, col, number in clues_coords:
            self._forward_checking((row, col), number, 'discard')

    def _forward_checking(self, coord: (int, int), entry: int, action: str) -> None:
        """
        Alters what values can go in each empty cell by either adding new values
        or getting rid of the certain values in the rows, columns or block.
        """
        self._alter_row(coord, entry, action)
        self._alter_col(coord, entry, action)
        self._alter_block(coord, entry, action)
    
    def _alter_history(self, coord: (int, int), action: str, entry: int) -> None:
        """
        Alters the set of values of an empty cell in the history dictionary
        by removing or adding the given entry/number.
        """
        if action == 'discard':
            self.pencil_marks[coord].discard(entry)
        else:
            self.pencil_marks[coord].add(entry)

    def _alter_row(self, coord: (int, int), entry: int, action: str) -> None:
        """
        Using the row number that is included in the given coordinate,
        it finds all the empty cells in the same row and manipulates their set
        of possible values.
        """
        row, _ = coord
        for pos in range(self._rows):
            if (row, pos) in self.pencil_marks:
                self._alter_history((row, pos), action, entry)
    
    def _alter_col(self, coord: (int, int), entry: int, action: str) -> None:
        """
        Using the column number that is included in the given coordinate,
        it finds all the empty cells in the same column and manipulates their set
        of possible values.
        """
        _, col = coord
        for pos in range(self._columns):
            if (pos, col) in self.pencil_marks:
                self._alter_history((pos, col), action, entry)

    def _alter_block(self, coord: (int, int), entry: int, action: str) -> None:
        """
        Using the given coordinate, it finds all the empty cells in the same block 
        and manipulates their set of possible values.
        """
        block = self.determine_block(coord)
        for pos in block:
            if pos in self.pencil_marks:
                self._alter_history(pos, action, entry)


if __name__ == '__main__':
    s = Sudoku()
    # s.generate_puzzle()
    # s.print_puzzle()
    s.webscrape_puzzle(('easy', 9))
    s.print_puzzle()
    print()
    # s._solve_puzzle()
    # s.print_puzzle()

    s.solve()
    s.print_puzzle()
    # s.generate_puzzle()
    # print(s._solve_puzzle())
    # print(s.zeros)
    # s.generate_puzzle()
    # s.print_puzzle()
