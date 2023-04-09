import time
from typing import Sequence

import pygame
from pygame import Surface

import linespy.events
from linespy.board import Board
from linespy.cell import Cell
from linespy.constants import (
    BALL_RADIUS,
    CELL_HEIGHT,
    CELL_WIDTH,
    GRID_LINE_COLOR,
    NUM_COLUMNS,
    NUM_ROWS,
    SCREEN_BACKGROUND_COLOR,
    SCREEN_SIZE,
)
from linespy.errors import CoordinatesBeyondGridError


def draw_grid(screen: Surface):
    # Draw vertical grid lines
    for x in range(40, 360, 40):
        pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, 360))

    # Draw horizontal grid lines
    for y in range(40, 360, 40):
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (360, y))


def draw_ball(screen: Surface, cell: Cell) -> None:
    color = cell.color
    if color is None:
        return

    center_y = (cell.row - 1) * CELL_HEIGHT + (CELL_HEIGHT // 2)
    center_x = (cell.column - 1) * CELL_WIDTH + (CELL_WIDTH // 2)

    pygame.draw.circle(
        screen, color=color, center=(center_x, center_y), radius=BALL_RADIUS
    )


def draw_selected_ball(screen: Surface, cell: Cell) -> None:
    """Draws an outline around the selected ball."""
    center_y = (cell.row - 1) * CELL_HEIGHT + (CELL_HEIGHT // 2)
    center_x = (cell.column - 1) * CELL_WIDTH + (CELL_WIDTH // 2)

    pygame.draw.circle(
        screen, color="white", center=(center_x, center_y), radius=BALL_RADIUS, width=3
    )


def clear_cell(screen: Surface, cell: Cell) -> None:
    """Clears the cell from a ball image."""

    # Add 1 for the grid line thickness.
    top_y = 1 + (cell.row - 1) * CELL_HEIGHT
    left_x = 1 + (cell.column - 1) * CELL_WIDTH

    # NOTE: pygame.Rect doesn't support keyword arguments.
    rect = pygame.Rect(left_x, top_y, CELL_WIDTH - 1, CELL_HEIGHT - 1)
    screen.fill(SCREEN_BACKGROUND_COLOR, rect)


def get_cell_column_and_row_by_screen_coords(x: int, y: int) -> tuple[int, int]:
    """Transforms screen coordinates to board coordinates.

    If clicked outside the board's grid, raises an error.
    """
    column = x // CELL_WIDTH + 1
    row = y // CELL_HEIGHT + 1
    if column > NUM_COLUMNS or row > NUM_ROWS:
        raise CoordinatesBeyondGridError
    return column, row


def handle_board_events(
    screen: Surface, events: Sequence[linespy.events.Event]
) -> bool:
    """Handles game board events and returns whether the game continues or not."""
    for event in events:
        match event:
            case linespy.events.GameOver():
                # TODO: play sound or otherwise signal to player that the game is over.
                return False
            case linespy.events.ImpossibleMove():
                # TODO: play sound or otherwise signal to player that the move is impossible.
                return True
            case linespy.events.LineCompleted(cells):
                # TODO: clear the specified cells
                pass
            case linespy.events.UpdateScore(score=score):
                # TODO: display player's new score on the HUD (create one!)
                print(f"New score: {score}")
            case linespy.events.AddBall(cell=cell):
                # Draw a ball to given cell.
                draw_ball(screen, cell)
                # Make a pause before rendering.
                pygame.time.wait(100)
            case linespy.events.SelectBall(cell=cell):
                # This matches the event's `cell` attribute to the local variable `cell`.
                draw_selected_ball(screen, cell)
            case linespy.events.DeselectBall(cell=cell):
                # Just redraw a regular ball.
                draw_ball(screen, cell)
            case linespy.events.MoveBall(from_cell=from_cell, to_cell=to_cell):
                clear_cell(screen, from_cell)
                draw_ball(screen, to_cell)
            case _:
                raise TypeError(f"Unknown event {event.__class__.__name__}")
        # after each update to the screen, re-draw it
        pygame.display.flip()

    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    time.sleep(0.1)
    screen.fill(SCREEN_BACKGROUND_COLOR)
    draw_grid(screen)
    pygame.display.flip()

    # init the board and handle initial events, such as adding a few balls
    board = Board.create(columns=NUM_COLUMNS, rows=NUM_ROWS)
    initial_events = board.handle_initialization()
    handle_board_events(screen, initial_events)

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONUP:
                    try:
                        column, row = get_cell_column_and_row_by_screen_coords(
                            *event.pos
                        )
                    except CoordinatesBeyondGridError:
                        print("Clicked", event.pos)
                        continue
                    print("Clicked cell", column, row)

                    # handle player action
                    board_events = board.handle_action(column, row)
                    running = handle_board_events(screen, board_events)
                    if not running:
                        print("Game over!")

                case pygame.QUIT:
                    running = False


if __name__ == "__main__":
    main()
