import dataclasses
import random
from typing import Self

from linespy.cell import Cell
from linespy.constants import BallColor
from linespy.errors import NoMoreFreeCellsError


@dataclasses.dataclass
class Board:
    """Represents the game board.

    A board contains references to cells, as a flat list (row after row).

    Attributes:
        cells: a flat list of cells ("Flat is better than nested" (c) the Zen of Python)
        columns: number of columns
        rows: number of rows
    """

    cells: list[Cell]
    columns: int
    rows: int

    @classmethod
    def create(cls, columns: int, rows: int) -> Self:
        """Creates a board with a specified number of columns and rows."""

        cells = [
            # nested for-loops in comprehensions
            # are semantically equivalent to normal nested for-loops.
            Cell(row=row + 1, column=column + 1)
            for row in range(rows)
            for column in range(columns)
        ]
        return cls(cells=cells, columns=columns, rows=rows)

    def add_random_ball(self) -> Cell:
        free_cells = [cell for cell in self.cells if cell.is_empty]
        if not free_cells:
            raise NoMoreFreeCellsError

        target_cell: Cell = random.choice(free_cells)
        color = random.choice([c for c in BallColor])

        target_cell.color = color
        return target_cell
