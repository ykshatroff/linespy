import dataclasses
import random
from typing import Self, Sequence

from linespy.cell import Cell
from linespy.constants import BallColor
from linespy.errors import NoMoreFreeCellsError
from linespy.events import DeselectBall, Event, ImpossibleMove, MoveBall, SelectBall


@dataclasses.dataclass
class Board:
    """Represents the game board.

    A board contains references to cells, as a flat list (row after row).

    Board instances support indexing: to get a cell at given column and row, just write

        board[column, row]

    Note that board coordinates are 1-based: the first cell is at (1, 1).

    Attributes:
        cells: a flat list of cells ("Flat is better than nested" (c) the Zen of Python)
        columns: number of columns
        rows: number of rows
        selected_cell: if any ball is selected, contains the ball's cell, otherwise None.
    """

    cells: list[Cell]
    columns: int
    rows: int
    selected_cell: Cell | None = None

    def __getitem__(self, column_and_row: tuple[int, int]) -> Cell:
        """Gets a cell by given tuple of (column, row) coordinates (1-based)."""
        column, row = column_and_row
        if not 1 <= column <= self.columns:
            raise KeyError(f"Invalid column number {column}, must be between 1 and {self.columns}")
        if not 1 <= row <= self.rows:
            raise KeyError(f"Invalid row number {row}, must be between 1 and {self.rows}")
        return self.cells[(column - 1) + (row - 1) * self.columns]

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

    def handle_action(self, column: int, row: int) -> Sequence[Event]:
        """Processes player click on a cell, emitting events.

        More on actions and events in the `events` module.
        """
        cell = self[column, row]
        if cell.is_empty:
            if self.selected_cell is None:
                return []
            else:
                events = self._handle_ball_move(
                    from_cell=self.selected_cell, to_cell=cell
                )

                # the selected ball becomes deselected after the move.
                self.selected_cell = None
                return events

        events = []
        if self.selected_cell is not None:
            # make sure we use self.selected_cell before it's changed!
            deselect_event = DeselectBall(cell=self.selected_cell)
            events.append(deselect_event)

        if self.selected_cell is cell:
            # just deselect the currently selected cell
            self.selected_cell = None
            return events
        else:
            # mark the clicked ball as the new selected one and deselect the previous one
            self.selected_cell = cell
            events.append(SelectBall(cell=cell))
            return events

    def _handle_ball_move(self, from_cell: Cell, to_cell: Cell) -> Sequence[Event]:
        """Handles the action of moving a ball.

        Emits (returns) the following events:
        * Single `ImpossibleMove` event if the ball cannot be moved to the target cell;
        * One or more `MoveBall` events according to the ball's path,
          and one or more `LineCompleted` events
        """
        path = self._evaluate_path(from_cell, to_cell)
        if not path:
            return [ImpossibleMove()]

        events: list[MoveBall] = []
        for pos, cell in enumerate(path[1:], 1):
            # make an event with source cell being the previous cell in path,
            # and destination cell being the current one.
            events.append(MoveBall(from_cell=path[pos - 1], to_cell=cell))
        return events

    def _evaluate_path(self, from_cell: Cell, to_cell: Cell) -> Sequence[Cell]:
        """Determines the path for the ball to move from one cell to another.

        If a path exists, return a series of cells starting from the origin cell
        and up to and including the destination cell.
        If a path doesn't exist, return an empty list.
        """
        # NOTE: in the absence of an implementation, this just returns
        #  the origin and destination cells, thus making any move possible.
        # TODO: use the shortest path algorithm to find a path.

        # Swap cell colors.
        # When we visualize the full path, we don't need to swap colors
        #  for every single cell on the path, because it makes no sense for the board;
        #  rather we should do it in the event handler in `main.py`,
        #  since it is only a detail relevant to the display.
        to_cell.color = from_cell.color
        from_cell.color = None
        return [from_cell, to_cell]
