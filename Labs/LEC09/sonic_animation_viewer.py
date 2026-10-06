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


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pass
    finally:
        close_canvas()


if __name__ == "__main__":
    main()