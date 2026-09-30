from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SPRITE_SHEET_PATH = "mario.png"
SHEET_WIDTH = 1456
SHEET_HEIGHT = 730
FRAME_COLUMNS = 12
FIRST_ACTION_TOP = 0
FIRST_ACTION_BOTTOM = 156


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
        clear_canvas()
        mario_sheet.clip_draw(0, 0, 1, 1, 400, 300, CANVAS_WIDTH, CANVAS_HEIGHT)
        mario_sheet.clip_draw(
            0,
            SHEET_HEIGHT - FIRST_ACTION_BOTTOM,
            SHEET_WIDTH // FRAME_COLUMNS,
            FIRST_ACTION_BOTTOM - FIRST_ACTION_TOP,
            400,
            300,
        )
        update_canvas()
        delay(0.01)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()