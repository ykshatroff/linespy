from enum import IntEnum

CELL_WIDTH = 40
CELL_HEIGHT = 40
NUM_ROWS = 9
NUM_COLUMNS = 9

SCREEN_SIZE = NUM_COLUMNS * CELL_WIDTH, NUM_ROWS * CELL_HEIGHT  # X, Y in pixels
SCREEN_BACKGROUND_COLOR = 100, 200, 255  # Red, Green, Blue (0-255)
GRID_LINE_COLOR = 255, 255, 255  # white
BALL_RADIUS = 16


class BallColor(IntEnum):
    RED = 0xCC0000  # 0xRRGGBB: Equivalent to tuple (204, 0, 0)
    GREEN = 0x00CC00
    BLUE = 0x0000CC
    MAGENTA = 0xCC00CC
    CYAN = 0x00CCCC
    YELLOW = 0xCCCC00
    BLACK = 0