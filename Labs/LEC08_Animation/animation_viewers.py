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


def validate_animations(animations, sheet_width, sheet_height):
    if not animations:
        raise ValueError("At least one animation is required")
    for animation in animations:
        if not animation:
            raise ValueError("Every animation must contain at least one frame")
        for frame in animation:
            if len(frame) != 4:
                raise ValueError("Frame rectangles must contain four values")
            left, bottom, width, height = frame
            if left < 0 or bottom < 0 or width <= 0 or height <= 0:
                raise ValueError("Frame rectangles must have positive in-bounds sizes")
            if left + width > sheet_width or bottom + height > sheet_height:
                raise ValueError("Frame rectangle is outside the sprite sheet")
    return animations


MARIO_ANIMATIONS = build_grid_animations(
    SHEET_WIDTH,
    SHEET_HEIGHT,
    ACTION_ROWS,
    (FRAME_COLUMNS,) * len(ACTION_ROWS),
)
MARIO_TRIMMED_ANIMATIONS = (
    (
        (20, 576, 76, 142), (142, 575, 76, 143), (264, 575, 76, 143),
        (386, 574, 76, 144), (506, 575, 79, 143), (628, 574, 76, 144),
        (750, 576, 76, 142), (875, 576, 79, 142), (990, 575, 77, 143),
        (1112, 575, 78, 143), (1235, 576, 77, 142), (1358, 575, 76, 143),
    ),
    (
        (20, 433, 76, 139), (142, 433, 76, 139), (268, 432, 72, 140),
        (392, 433, 66, 139), (513, 432, 71, 140), (634, 432, 70, 140),
        (753, 432, 70, 140), (875, 431, 73, 141), (997, 435, 69, 137),
        (1116, 432, 71, 140), (1242, 434, 68, 138), (1357, 433, 77, 139),
    ),
    (
        (9, 297, 101, 130), (130, 296, 103, 133), (252, 298, 105, 130),
        (376, 296, 101, 133), (497, 298, 103, 129), (617, 295, 101, 134),
        (738, 296, 102, 131), (859, 296, 104, 131), (980, 295, 102, 134),
        (1100, 298, 104, 131), (1226, 297, 101, 132), (1347, 296, 103, 133),
    ),
    (
        (22, 135, 73, 119), (144, 135, 72, 121), (267, 135, 70, 126),
        (381, 142, 84, 129), (502, 154, 86, 129), (626, 158, 84, 132),
        (744, 166, 85, 126), (867, 157, 89, 131), (988, 147, 87, 130),
        (1120, 135, 68, 126), (1238, 137, 72, 121), (1357, 137, 83, 124),
    ),
    (
        (0, 14, 120, 113), (123, 3, 117, 94), (244, 4, 120, 123),
        (367, 0, 118, 123), (485, 16, 121, 108), (607, 13, 121, 109),
        (729, 14, 120, 87), (852, 4, 118, 123), (970, 0, 122, 108),
        (1092, 16, 121, 108), (1213, 14, 121, 103), (1336, 11, 120, 106),
    ),
)


class AnimationState:
    def __init__(self, animations=MARIO_TRIMMED_ANIMATIONS):
        self.animations = animations
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


def get_frame_rect(action_index, frame_index, animations=MARIO_TRIMMED_ANIMATIONS):
    if not 0 <= action_index < len(animations):
        raise IndexError("Action index is outside the animation list")
    if not 0 <= frame_index < len(animations[action_index]):
        raise IndexError("Frame index is outside the action")
    return animations[action_index][frame_index]


def draw_action_frame(
    mario_sheet,
    action_index,
    frame_index,
    animations=MARIO_TRIMMED_ANIMATIONS,
):
    frame_left, frame_bottom, frame_width, frame_height = get_frame_rect(
        action_index,
        frame_index,
        animations,
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
        frame_count = len(state.animations[state.action_index])
        state.frame_index, state.completed_playbacks = advance_playback_frame(
            state.frame_index,
            state.completed_playbacks,
            frame_count,
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
            len(state.animations),
        )
        state.frame_index = 0
        state.completed_playbacks = 0
        state.phase = PLAYING
        state.next_frame_time = now
    return None


def main(animations=MARIO_TRIMMED_ANIMATIONS):
    validate_animations(animations, SHEET_WIDTH, SHEET_HEIGHT)
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    mario_sheet = None
    try:
        mario_sheet = load_image(SPRITE_SHEET_PATH)
        state = AnimationState(animations)
        while True:
            if should_quit(get_events()):
                break

            frame_to_draw = update_animation(state, monotonic())
            if frame_to_draw is not None:
                draw_action_frame(mario_sheet, *frame_to_draw, state.animations)
            delay(0.005)
    finally:
        mario_sheet = None
        close_canvas()


if __name__ == "__main__":
    main()