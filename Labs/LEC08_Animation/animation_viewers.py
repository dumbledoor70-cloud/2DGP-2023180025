from time import monotonic

from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SPRITE_SHEET_PATH = "mario.png"
SHEET_WIDTH = 1456
SHEET_HEIGHT = 730
FRAME_COLUMNS = 12
ACTION_ROWS = (
    (0, 156),
    (156, 300),
    (300, 436),
    (436, 598),
    (598, 730),
)
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2
MAX_DISPLAY_WIDTH = 420
MAX_DISPLAY_HEIGHT = 460
FRAME_INTERVAL_SECONDS = 0.1
ACTION_REPEAT_COUNT = 5
ACTION_PAUSE_SECONDS = 1.0
PLAYING = "playing"
PAUSING = "pausing"
FrameRect = tuple[int, int, int, int]
AnimationFrames = tuple[FrameRect, ...]


def build_grid_animations(sheet_width, sheet_height, action_rows, frame_counts):
    animations = []
    for (top, bottom), frame_count in zip(action_rows, frame_counts):
        frames = []
        for frame_index in range(frame_count):
            left = frame_index * sheet_width // frame_count
            right = (frame_index + 1) * sheet_width // frame_count
            frames.append((left, sheet_height - bottom, right - left, bottom - top))
        animations.append(tuple(frames))
    return tuple(animations)


class AnimationState:
    def __init__(self):
        self.action_index = 0
        self.frame_index = 0
        self.completed_playbacks = 0
        self.phase = PLAYING
        self.next_frame_time = 0.0
        self.pause_until = 0.0


def next_frame_index(frame_index, frame_count):
    return (frame_index + 1) % frame_count


def advance_playback_frame(frame_index, completed_playbacks, frame_count):
    next_index = next_frame_index(frame_index, frame_count)
    if next_index == 0:
        completed_playbacks += 1
    return next_index, completed_playbacks


def next_action_index(action_index, action_count):
    return (action_index + 1) % action_count


def should_quit(events):
    for event in events:
        if event.type == SDL_QUIT:
            return True
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return True
    return False


def calculate_display_size(frame_width, frame_height):
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("Frame dimensions must be positive")
    scale = min(
        MAX_DISPLAY_WIDTH / frame_width,
        MAX_DISPLAY_HEIGHT / frame_height,
    )
    return round(frame_width * scale), round(frame_height * scale)


def get_frame_rect(action_index, frame_index):
    if not 0 <= action_index < len(ACTION_ROWS):
        raise IndexError("Action index is outside the sprite sheet")
    if not 0 <= frame_index < FRAME_COLUMNS:
        raise IndexError("Frame index is outside the action")

    action_top, action_bottom = ACTION_ROWS[action_index]
    frame_left = frame_index * SHEET_WIDTH // FRAME_COLUMNS
    next_frame_left = (frame_index + 1) * SHEET_WIDTH // FRAME_COLUMNS
    frame_bottom = SHEET_HEIGHT - action_bottom
    frame_width = next_frame_left - frame_left
    frame_height = action_bottom - action_top
    if (
        frame_left < 0
        or frame_bottom < 0
        or frame_left + frame_width > SHEET_WIDTH
        or frame_bottom + frame_height > SHEET_HEIGHT
    ):
        raise ValueError("Frame rectangle is outside the sprite sheet")
    return frame_left, frame_bottom, frame_width, frame_height


def draw_action_frame(mario_sheet, action_index, frame_index):
    frame_left, frame_bottom, frame_width, frame_height = get_frame_rect(
        action_index,
        frame_index,
    )
    display_width, display_height = calculate_display_size(
        frame_width,
        frame_height,
    )

    clear_canvas()
    mario_sheet.clip_draw(
        0,
        0,
        1,
        1,
        CENTER_X,
        CENTER_Y,
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    )
    mario_sheet.clip_draw(
        frame_left,
        frame_bottom,
        frame_width,
        frame_height,
        CENTER_X,
        CENTER_Y,
        display_width,
        display_height,
    )
    update_canvas()


def update_animation(state, now):
    if state.phase == PLAYING:
        if now < state.next_frame_time:
            return None

        frame_to_draw = (state.action_index, state.frame_index)
        state.frame_index, state.completed_playbacks = advance_playback_frame(
            state.frame_index,
            state.completed_playbacks,
            FRAME_COLUMNS,
        )
        if state.completed_playbacks == ACTION_REPEAT_COUNT:
            state.phase = PAUSING
            state.pause_until = now + ACTION_PAUSE_SECONDS
        else:
            state.next_frame_time = now + FRAME_INTERVAL_SECONDS
        return frame_to_draw

    if state.phase == PAUSING and now >= state.pause_until:
        state.action_index = next_action_index(
            state.action_index,
            len(ACTION_ROWS),
        )
        state.frame_index = 0
        state.completed_playbacks = 0
        state.phase = PLAYING
        state.next_frame_time = now
    return None


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    mario_sheet = None
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
        state = AnimationState()
        while True:
            if should_quit(get_events()):
                break

            frame_to_draw = update_animation(state, monotonic())
            if frame_to_draw is not None:
                draw_action_frame(mario_sheet, *frame_to_draw)
            delay(0.005)
    finally:
        mario_sheet = None
        close_canvas()


if __name__ == "__main__":
    main()