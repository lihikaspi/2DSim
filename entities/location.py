from dataclasses import dataclass


@dataclass
class Location:
    row: int
    col: int

    @property
    def coords(self) -> tuple[int, int]:
        return self.row, self.col
