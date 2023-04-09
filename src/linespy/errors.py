class LinesPyError(Exception):
    """A base error class for all errors happening in the game."""


class NoMoreFreeCellsError(LinesPyError):
    """Raised when no more balls can be added."""


class CoordinatesBeyondGridError(LinesPyError):
    """Raised when screen-based pixel coordinates are outside of the board's grid."""
