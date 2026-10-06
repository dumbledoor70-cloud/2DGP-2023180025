import unittest
from unittest.mock import patch

import sonic_animation_viewer as viewer


class ViewerSetupTests(unittest.TestCase):
    def test_canvas_dimensions_match_prd(self):
        self.assertEqual((viewer.CANVAS_WIDTH, viewer.CANVAS_HEIGHT), (1200, 600))

    def test_playback_settings_match_prd(self):
        self.assertEqual(viewer.FRAME_INTERVAL_SECONDS, 0.1)
        self.assertEqual(viewer.ACTION_REPEAT_COUNT, 5)
        self.assertEqual(viewer.ACTION_PAUSE_SECONDS, 0.5)
        self.assertEqual(viewer.MOVEMENT_SPEED, 120.0)

    def test_frame_rect_converts_top_origin_to_pico2d_origin(self):
        frame = viewer.FrameRect(10, 20, 30, 40)

        self.assertEqual(frame.to_pico2d(525), (10, 465, 30, 40))

    def test_animation_action_stores_variable_frames_and_direction(self):
        action = viewer.AnimationAction(
            "run_right",
            (viewer.FrameRect(0, 0, 30, 40), viewer.FrameRect(30, 2, 28, 38)),
            direction_x=1,
        )

        self.assertEqual(len(action.frames), 2)
        self.assertEqual((action.direction_x, action.direction_y), (1, 0))

    def test_main_opens_and_closes_canvas(self):
        with (
            patch.object(viewer, "open_canvas") as open_canvas,
            patch.object(viewer, "close_canvas") as close_canvas,
        ):
            viewer.main()

        open_canvas.assert_called_once_with(1200, 600)
        close_canvas.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()