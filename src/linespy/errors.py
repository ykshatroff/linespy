class LinesPyError(Exception):
    """A base error class for all errors happening in the game."""


class NoMoreFreeCellsError(LinesPyError):
    """Raised when no more balls can be added."""
