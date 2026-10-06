from dataclasses import dataclass
from typing import NamedTuple

from pico2d import close_canvas, open_canvas


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 600
FRAME_INTERVAL_SECONDS = 0.1
ACTION_REPEAT_COUNT = 5
ACTION_PAUSE_SECONDS = 0.5
MOVEMENT_SPEED = 120.0


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


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pass
    finally:
        close_canvas()


if __name__ == "__main__":
    main()