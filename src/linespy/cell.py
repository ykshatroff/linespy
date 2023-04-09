import dataclasses

from linespy.constants import BallColor


@dataclasses.dataclass
class Cell:
    """Represents a cell on the board.

    A cell can contain a ball of one of `BallColor` colors, or be empty.

    Cell's column and row are 1-based for the sake of ease to display to the player.

    Attributes:
        row: row number, 1-based, starting from top
        column: column number, 1-based, starting from left
        color: one of an enumeration of available colors, or None if cell is empty
    """

    row: int
    column: int
    color: BallColor | None = None

    @property
    def is_empty(self) -> bool:
        return self.color is None

    def __repr__(self):
        return f"Cell({self.column}, {self.row})"
