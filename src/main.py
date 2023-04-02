import time

import pygame

SCREEN_SIZE = 360, 360  # X, Y in pixels
SCREEN_BACKGROUND_COLOR = 100, 200, 255  # Red, Green, Blue (0-255)
GRID_LINE_COLOR = 255, 255, 255  # white


def draw_grid(screen):
    # Draw vertical grid lines
    for x in range(40, 360, 40):
        pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, 360))

    # Draw horizontal grid lines
    for y in range(40, 360, 40):
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (360, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    time.sleep(0.1)
    screen.fill(SCREEN_BACKGROUND_COLOR)
    draw_grid(screen)
    pygame.display.flip()

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONUP:
                    print("Clicked", event.pos)

                case pygame.QUIT:
                    running = False


if __name__ == '__main__':
    main()
