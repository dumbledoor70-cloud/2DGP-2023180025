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


def next_frame_index(frame_index, frame_count):
    return (frame_index + 1) % frame_count


def calculate_display_size(frame_width, frame_height):
    scale = min(
        MAX_DISPLAY_WIDTH / frame_width,
        MAX_DISPLAY_HEIGHT / frame_height,
    )
    return round(frame_width * scale), round(frame_height * scale)


def draw_first_action_frame(mario_sheet, frame_index):
    frame_left = frame_index * SHEET_WIDTH // FRAME_COLUMNS
    next_frame_left = (frame_index + 1) * SHEET_WIDTH // FRAME_COLUMNS
    frame_width = next_frame_left - frame_left
    frame_height = FIRST_ACTION_BOTTOM - FIRST_ACTION_TOP
    display_width, display_height = calculate_display_size(
        frame_width,
        frame_height,
    )

    clear_canvas()
    mario_sheet.clip_draw(0, 0, 1, 1, CENTER_X, CENTER_Y, CANVAS_WIDTH, CANVAS_HEIGHT)
    mario_sheet.clip_draw(
        frame_left,
        SHEET_HEIGHT - FIRST_ACTION_BOTTOM,
        frame_width,
        frame_height,
        CENTER_X,
        CENTER_Y,
        display_width,
        display_height,
    )
    update_canvas()


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
        frame_index = 0
        frames_drawn = 0
        while frames_drawn < FRAME_COLUMNS:
            draw_first_action_frame(mario_sheet, frame_index)
            frame_index = next_frame_index(frame_index, FRAME_COLUMNS)
            frames_drawn += 1
            delay(0.1)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()