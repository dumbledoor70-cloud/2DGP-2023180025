from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SPRITE_SHEET_PATH = "mario.png"


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()