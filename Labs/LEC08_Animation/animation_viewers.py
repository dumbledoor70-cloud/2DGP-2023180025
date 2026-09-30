from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SPRITE_SHEET_PATH = "mario.png"
SHEET_WIDTH = 1456
SHEET_HEIGHT = 730
FRAME_COLUMNS = 12
FIRST_ACTION_TOP = 0
FIRST_ACTION_BOTTOM = 156
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2
MAX_DISPLAY_WIDTH = 420
MAX_DISPLAY_HEIGHT = 460


def calculate_display_size(frame_width, frame_height):
    scale = min(
        MAX_DISPLAY_WIDTH / frame_width,
        MAX_DISPLAY_HEIGHT / frame_height,
    )
    return round(frame_width * scale), round(frame_height * scale)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
        clear_canvas()
        mario_sheet.clip_draw(0, 0, 1, 1, 400, 300, CANVAS_WIDTH, CANVAS_HEIGHT)
        frame_width = SHEET_WIDTH // FRAME_COLUMNS
        frame_height = FIRST_ACTION_BOTTOM - FIRST_ACTION_TOP
        display_width, display_height = calculate_display_size(
            frame_width,
            frame_height,
        )
        mario_sheet.clip_draw(
            0,
            SHEET_HEIGHT - FIRST_ACTION_BOTTOM,
            frame_width,
            frame_height,
            CENTER_X,
            CENTER_Y,
            display_width,
            display_height,
        )
        update_canvas()
        delay(0.01)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()