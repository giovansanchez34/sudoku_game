from bs4 import BeautifulSoup
from re import search
import urllib.request
import urllib.error


def _get_puzzle_id(soup: BeautifulSoup) -> str:
    """Returns the id number of the puzzle."""

    grid = soup.find_all('div', 'grid')[0].text
    return search(r'(\d{2,})', grid).group(1).strip()


def _get_url(response: str, id_number: int) -> str:
    """Returns the correct url based on the given response."""
    if response == 'solution':
        return f'http://www.menneske.no/sudoku/eng/solution.html?number={id_number}'
    else:
        return f'http://www.menneske.no/sudoku/eng/random.html?diff={id_number}'


def get_sudoku_puzzle(response: (str, str), board: [[int]]) -> str:
    """Gets the sudoku puzzle from the website."""

    puzzle_url = _get_url(*response)
    soup = _scrape_puzzle(puzzle_url)
    _construct_sudoku(soup, board)
    return _get_puzzle_id(soup)


def get_sudoku_solution(response: (str, int), board: [[int]]) -> None:
    """Gets the solution to the sudoku puzzle that was scraped from the website."""
    solution_url = _get_url(*response)
    soup = _scrape_puzzle(solution_url)
    _construct_sudoku(soup, board)


def _scrape_puzzle(url: str) -> BeautifulSoup:
    """
    Returns a beautiful soup object that contains
    data that was scraped from the url.
    """
    while True:
        response = None
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            soup = BeautifulSoup(data, 'lxml')
            return soup
        except urllib.error:
            pass
        finally:
            if response is not None:
                response.close()


def _construct_sudoku(soup: BeautifulSoup, board: [[int]]) -> None:
    """
    Based on the given beautiful soup object, it
    construct either the solution to a sudoku puzzle or
    constructs a sudoku puzzle. The given board is mutated.
    """
    grid_rows = soup.find_all('tr', 'grid')
    for row_pos, grid_row in enumerate(grid_rows):
        entries = grid_row.find_all('td')
        for col_pos, entry in enumerate(entries):
            if entry.text != '\xa0':
                board[row_pos][col_pos] = int(entry.text)
            else:
                board[row_pos][col_pos] = 0


#get_sudoku_puzzle(('easy', 3), [[0] * 9 for row in range(9)])
