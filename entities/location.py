from typing import Tuple

class Location:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.coords = (row, col)