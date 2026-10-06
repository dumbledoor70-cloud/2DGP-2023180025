from dataclasses import dataclass
from typing import NamedTuple

from pico2d import clear_canvas, close_canvas, load_image, open_canvas, update_canvas


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 600
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2
SPRITE_SHEET_PATH = "sonic-sprite.png"
SHEET_WIDTH = 399
SHEET_HEIGHT = 525
FRAME_INTERVAL_SECONDS = 0.1
ACTION_REPEAT_COUNT = 5
ACTION_PAUSE_SECONDS = 0.5
MOVEMENT_SPEED = 120.0
PLAYING = "playing"
PAUSING = "pausing"


class FrameRect(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    def to_pico2d(self, sheet_height):
        return self.x, sheet_height - self.y - self.height, self.width, self.height


@dataclass(frozen=True)
class AnimationAction:
    name: str
    frames: tuple[FrameRect, ...]
    direction_x: int = 0
    direction_y: int = 0


RUN_RIGHT_FRAMES = (
    FrameRect(1, 39, 29, 39),
    FrameRect(31, 40, 26, 38),
    FrameRect(58, 39, 28, 39),
    FrameRect(86, 40, 30, 38),
    FrameRect(118, 40, 30, 38),
    FrameRect(150, 40, 30, 38),
    FrameRect(182, 40, 29, 38),
    FrameRect(211, 39, 29, 38),
    FrameRect(240, 39, 29, 38),
    FrameRect(270, 45, 24, 32),
    FrameRect(302, 51, 29, 26),
)
RUN_RIGHT_ALT_FRAMES = (
    FrameRect(8, 80, 26, 37),
    FrameRect(37, 80, 27, 37),
    FrameRect(65, 80, 31, 38),
    FrameRect(97, 80, 37, 37),
    FrameRect(135, 80, 32, 35),
    FrameRect(170, 79, 32, 38),
    FrameRect(206, 79, 26, 38),
    FrameRect(238, 80, 24, 37),
    FrameRect(263, 80, 30, 37),
    FrameRect(295, 80, 36, 37),
    FrameRect(334, 80, 32, 36),
    FrameRect(370, 79, 29, 38),
)
JUMP_FRAMES = (
    FrameRect(1, 124, 33, 40),
    FrameRect(39, 124, 35, 39),
    FrameRect(89, 125, 35, 38),
    FrameRect(130, 121, 34, 42),
    FrameRect(181, 122, 34, 41),
    FrameRect(228, 122, 33, 40),
)
ACTION_4_FRAMES = (
    FrameRect(1, 169, 29, 30),
    FrameRect(35, 167, 29, 31),
    FrameRect(67, 169, 30, 29),
    FrameRect(98, 169, 31, 29),
    FrameRect(131, 168, 29, 30),
    FrameRect(162, 168, 29, 31),
    FrameRect(193, 170, 30, 29),
    FrameRect(230, 170, 31, 29),
    FrameRect(268, 170, 30, 30),
)
ACTION_5_FRAMES = (
    FrameRect(1, 206, 30, 27),
    FrameRect(36, 206, 29, 27),
    FrameRect(70, 206, 29, 27),
    FrameRect(105, 206, 29, 27),
    FrameRect(139, 206, 29, 27),
    FrameRect(174, 206, 29, 27),
)
ACTION_6_FRAMES = (
    FrameRect(1, 239, 29, 35),
    FrameRect(36, 239, 30, 35),
    FrameRect(74, 239, 31, 35),
    FrameRect(111, 238, 31, 36),
    FrameRect(149, 239, 30, 35),
    FrameRect(186, 238, 31, 36),
)
ACTION_7_FRAMES = (
    FrameRect(1, 283, 29, 35),
    FrameRect(36, 283, 30, 35),
    FrameRect(72, 286, 39, 31),
    FrameRect(123, 285, 39, 32),
    FrameRect(172, 286, 39, 31),
    FrameRect(218, 285, 38, 32),
)
ACTION_8_FRAMES = (
    FrameRect(1, 326, 24, 45),
    FrameRect(31, 327, 29, 44),
    FrameRect(65, 327, 20, 44),
    FrameRect(90, 327, 25, 43),
    FrameRect(119, 327, 25, 43),
    FrameRect(149, 327, 20, 44),
    FrameRect(184, 341, 40, 28),
    FrameRect(232, 341, 39, 27),
)
SONIC_ACTIONS = (
    AnimationAction("동작 1", RUN_RIGHT_FRAMES, direction_x=1),
    AnimationAction("동작 2", RUN_RIGHT_ALT_FRAMES, direction_x=1),
    AnimationAction("동작 3", JUMP_FRAMES),
    AnimationAction("동작 4", ACTION_4_FRAMES),
    AnimationAction("동작 5", ACTION_5_FRAMES),
    AnimationAction("동작 6", ACTION_6_FRAMES),
    AnimationAction("동작 7", ACTION_7_FRAMES),
    AnimationAction("동작 8", ACTION_8_FRAMES),
)


class AnimationState:
    def __init__(self, actions=SONIC_ACTIONS):
        validate_actions(actions)
        self.actions = actions
        self.action_index = 0
        self.frame_index = 0
        self.completed_repeats = 0
        self.phase = PLAYING
        self.x = CENTER_X
        self.y = CENTER_Y
        self.next_frame_time = 0.0
        self.pause_until = 0.0


def advance_frame_index(frame_index, frame_count):
    next_index = (frame_index + 1) % frame_count
    return next_index, next_index == 0


def update_animation(state, now):
    if state.phase == PLAYING:
        if now < state.next_frame_time:
            return None

        action = state.actions[state.action_index]
        frame = action.frames[state.frame_index]
        state.frame_index, completed_cycle = advance_frame_index(
            state.frame_index,
            len(action.frames),
        )
        if completed_cycle:
            state.completed_repeats += 1
        if state.completed_repeats == ACTION_REPEAT_COUNT:
            state.phase = PAUSING
            state.pause_until = now + ACTION_PAUSE_SECONDS
        else:
            state.next_frame_time = now + FRAME_INTERVAL_SECONDS
        return action, frame

    if state.phase == PAUSING and now >= state.pause_until:
        state.action_index = (state.action_index + 1) % len(state.actions)
        state.frame_index = 0
        state.completed_repeats = 0
        state.phase = PLAYING
        state.next_frame_time = now
    return None


def update_position(state, elapsed_seconds):
    if elapsed_seconds < 0:
        raise ValueError("Elapsed time cannot be negative")
    action = state.actions[state.action_index]
    state.x += action.direction_x * MOVEMENT_SPEED * elapsed_seconds
    state.y += action.direction_y * MOVEMENT_SPEED * elapsed_seconds
    return state.x, state.y


def clamp_position(state, canvas_width=CANVAS_WIDTH, canvas_height=CANVAS_HEIGHT):
    action = state.actions[state.action_index]
    max_width = max(get_display_size(frame)[0] for frame in action.frames)
    max_height = max(get_display_size(frame)[1] for frame in action.frames)
    half_width = max_width / 2
    half_height = max_height / 2
    if half_width * 2 > canvas_width or half_height * 2 > canvas_height:
        raise ValueError("Scaled Sonic frame is larger than the canvas")
    state.x = min(max(state.x, half_width), canvas_width - half_width)
    state.y = min(max(state.y, half_height), canvas_height - half_height)
    return state.x, state.y


def validate_actions(actions=SONIC_ACTIONS):
    if not actions:
        raise ValueError("At least one action is required")
    for action in actions:
        if not action.frames:
            raise ValueError(f"Action {action.name} must contain frames")
        for frame in action.frames:
            if frame.x < 0 or frame.y < 0 or frame.width <= 0 or frame.height <= 0:
                raise ValueError(f"Invalid frame rectangle in {action.name}")
            if frame.x + frame.width > SHEET_WIDTH or frame.y + frame.height > SHEET_HEIGHT:
                raise ValueError(f"Frame rectangle outside sprite sheet in {action.name}")
    return actions


def get_display_size(frame):
    return frame.width * 3, frame.height * 3


def draw_frame(sprite_sheet, frame, center_x=CENTER_X, center_y=CENTER_Y):
    source_rect = frame.to_pico2d(SHEET_HEIGHT)
    display_width, display_height = get_display_size(frame)
    clear_canvas()
    sprite_sheet.clip_draw(
        *source_rect,
        center_x,
        center_y,
        display_width,
        display_height,
    )
    update_canvas()


def load_sprite_sheet(path=SPRITE_SHEET_PATH):
    return load_image(path)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pass
    finally:
        close_canvas()


if __name__ == "__main__":
    main()