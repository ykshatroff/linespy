import time

import pygame
from pygame import Surface

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


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    time.sleep(0.1)
    screen.fill(SCREEN_BACKGROUND_COLOR)
    draw_grid(screen)
    pygame.display.flip()

    # init the board and add a few balls
    board = Board.create(columns=NUM_COLUMNS, rows=NUM_ROWS)
    for _ in range(3):
        cell = board.add_random_ball()
        draw_ball(screen, cell)
        # after each update to the screen, re-draw it
        pygame.display.flip()
        pygame.time.wait(50)

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONUP:
                    print("Clicked", event.pos)

                case pygame.QUIT:
                    running = False


if __name__ == "__main__":
    main()
