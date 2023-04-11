import dataclasses
import random
from typing import Self, Sequence

from linespy.cell import Cell
from linespy.constants import MIN_BALLS_IN_LINE, BallColor
from linespy.errors import NoMoreFreeCellsError
from linespy.events import (
    AddBall,
    DeselectBall,
    Event,
    GameOver,
    ImpossibleMove,
    LineCompleted,
    MoveBall,
    SelectBall,
    UpdateScore,
)


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
    score: int = 0

    def __getitem__(self, column_and_row: tuple[int, int]) -> Cell:
        """Gets a cell by given tuple of (column, row) coordinates (1-based)."""
        column, row = column_and_row
        if not 1 <= column <= self.columns:
            raise KeyError(
                f"Invalid column number {column}, must be between 1 and {self.columns}"
            )
        if not 1 <= row <= self.rows:
            raise KeyError(
                f"Invalid row number {row}, must be between 1 and {self.rows}"
            )
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

    def _add_random_ball(self) -> Cell:
        free_cells = [cell for cell in self.cells if cell.is_empty]
        if not free_cells:
            raise NoMoreFreeCellsError

        target_cell: Cell = random.choice(free_cells)
        color = random.choice([c for c in BallColor])

        target_cell.color = color
        return target_cell

    def _add_balls(self) -> Sequence[AddBall | GameOver]:
        """Adds 3 random balls."""
        events: list[AddBall | GameOver] = []
        for _ in range(3):
            events.append(AddBall(cell=self._add_random_ball()))
            # If there are no empty cells left, add a GameOver event
            #  and stop adding balls.
            if not any(cell for cell in self.cells if cell.is_empty):
                events.append(GameOver())
                break
        return events

    def handle_initialization(self) -> Sequence[Event]:
        """Produces events on board initialization."""
        return self._add_balls()

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

                if events != [ImpossibleMove()]:
                    # the selected ball becomes deselected after a successful move.
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

        events: list[Event] = [MoveBall(path=path)]

        formed_lines = self._evaluate_lines(to_cell)
        if formed_lines:
            for cell in formed_lines:
                cell.color = None

            events.append(LineCompleted(cells=formed_lines))

            # Use a simple counter of removed balls as score.
            # It can also be more sophisticated, such as:
            # * a premium for each ball above 5,
            # * a progressive premium (2 for 6th ball, 3 for 7th etc.)
            self.score += len(formed_lines)
            events.append(UpdateScore(self.score))

        else:
            # add new balls after a move that did not result in forming a line
            events += self._add_balls()
        return events

    def _evaluate_path(self, from_cell: Cell, to_cell: Cell) -> Sequence[Cell]:
        """Determines the path for the ball to move from one cell to another.

        If a path exists, return a series of cells starting from the origin cell
        and up to and including the destination cell.
        If a path doesn't exist, return an empty list.
        """

        # Reset any attributes left from previous path evaluation
        for cell in self.cells:
            cell.cost = None
            cell.previous_cell = None

        # The distance cost for the starting cell is 0.
        from_cell.cost = 0
        stack = [from_cell]

        def visit_cell(cell: Cell, previous_cell: Cell) -> None:
            assert previous_cell.cost is not None, "Previous cell should have been visited."
            if cell.is_empty:
                if cell.cost is None or cell.cost > previous_cell.cost + 1:
                    # Put the cell on the main pipeline queue
                    stack.append(cell)
                    cell.previous_cell = previous_cell
                    cell.cost = previous_cell.cost + 1

        while stack:
            last_cell = stack.pop()
            try:
                cell_up = self[last_cell.column, last_cell.row - 1]
            except KeyError:
                pass
            else:
                visit_cell(cell_up, last_cell)
            try:
                cell_down = self[last_cell.column, last_cell.row + 1]
            except KeyError:
                pass
            else:
                visit_cell(cell_down, last_cell)
            try:
                cell_left = self[last_cell.column - 1, last_cell.row]
            except KeyError:
                pass
            else:
                visit_cell(cell_left, last_cell)
            try:
                cell_right = self[last_cell.column + 1, last_cell.row]
            except KeyError:
                pass
            else:
                visit_cell(cell_right, last_cell)

        if to_cell.previous_cell is None:
            # We weren't able to find a path from target to source.
            return []

        path = [to_cell]
        start_cell: Cell | None = to_cell
        while (start_cell := start_cell.previous_cell) is not None:
            path.insert(0, start_cell)

        assert path[0] is from_cell, "We should get back to the starting cell."

        # Swap cell colors.
        # When we visualize the full path, we don't need to swap colors
        #  for every single cell on the path, because it makes no sense for the board;
        #  rather we should do it in the event handler in `main.py`,
        #  since it is only a detail relevant to the display.
        to_cell.color = from_cell.color
        from_cell.color = None

        return path

    def _evaluate_lines(self, cell: Cell) -> Sequence[Cell]:
        """Evaluates completed lines and returns cells belonging to them."""

        # We can use self[column, row] to access cells, allowing for simple iteration
        #  over cells in one row or column.
        # This implicitly calls Board.__getitem__().
        assert self[cell.column, cell.row] is cell

        v_line = [cell]
        for row in range(cell.row - 1, 0, -1):
            next_cell_up = self[cell.column, row]
            if next_cell_up.color == cell.color:
                v_line.insert(0, next_cell_up)
            else:
                break
        for row in range(cell.row + 1, self.rows + 1, 1):
            next_cell_down = self[cell.column, row]
            if next_cell_down.color == cell.color:
                v_line.append(next_cell_down)
            else:
                break

        h_line = [cell]
        for column in range(cell.column - 1, 0, -1):
            next_cell_left = self[column, cell.row]
            if next_cell_left.color == cell.color:
                h_line.insert(0, next_cell_left)
            else:
                break
        for column in range(cell.column + 1, self.columns + 1, 1):
            next_cell_right = self[column, cell.row]
            if next_cell_right.color == cell.color:
                h_line.append(next_cell_right)
            else:
                break

        # TODO: add diagonal lines

        result = []
        if len(h_line) >= MIN_BALLS_IN_LINE:
            result += h_line
        if len(v_line) >= MIN_BALLS_IN_LINE:
            result += v_line

        return result
