"""
Module for player events.

An event is a change of the board's state due to a player action.

Player actions in Lines can be of three kinds, according to the table:
                  |                   |
is ball selected? | ball clicked      | empty cell clicked
------------------------------------------------------------
             no   | select the ball   | -
------------------------------------------------------------
             yes  | deselect the ball | try to move selected ball
                  |                   | to the cell
 was the selected | if another ball   |
 ball clicked,    | was clicked,      |
 or a different   | select that ball  |
 one?             | instead

* select a ball
* deselect the selected ball
* try to move the selected ball to a chosen empty cell

The first two actions can emit one event each: select or deselect a ball, respectively.
But the action of selecting a ball can also emit two events:
select one ball and deselect another.

The third action, moving a ball from cell 1 to cell 2, can emit several types of events:
* To visualize the path of the ball from cell 1 to cell 2,
  we treat each advance to next cell as a separate event.
* In the beginning, for simplicity, we can just move the ball,
  emitting an event signifying the disappearance of the ball
  from cell 1 and its appearance in cell 2.
* If the ball, when placed in the target cell, forms a straight line or lines
  of 5 or more balls of the same color, these lines should be cleared and
  score should accrue to the player.
* When the path is blocked, this results in an event of type "move impossible".
  It may or may not result in visible changes, in an advanced version of the game
  it could for instance play a sound.

"""
import dataclasses
from typing import Sequence

from linespy.cell import Cell


class Event:
    """Base class for game board events."""


@dataclasses.dataclass
class AddBall(Event):
    """Points to a cell where a new ball is added."""

    cell: Cell


@dataclasses.dataclass
class GameOver(Event):
    """Emitted when no more empty cells are left on the board."""


@dataclasses.dataclass
class SelectBall(Event):
    cell: Cell


@dataclasses.dataclass
class DeselectBall(Event):
    cell: Cell


@dataclasses.dataclass
class MoveBall(Event):
    """Points to cells from which and to which the ball is moved.

    This is a simplified event, for demo purposes - it doesn't contain the full path.
    """

    from_cell: Cell
    to_cell: Cell


@dataclasses.dataclass
class LineCompleted(Event):
    """Points to cells with balls that formed a line of same color."""

    cells: Sequence[Cell]


@dataclasses.dataclass
class ImpossibleMove(Event):
    """Signifies that there is no path from one cell to another.

    Doesn't need any attributes because there are no visible effects.
    """
