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

    def test_first_run_action_has_eleven_explicit_frames(self):
        self.assertEqual(len(viewer.RUN_RIGHT_FRAMES), 11)
        self.assertEqual(viewer.RUN_RIGHT_FRAMES[0], viewer.FrameRect(1, 39, 29, 39))
        self.assertEqual(viewer.RUN_RIGHT_FRAMES[-1], viewer.FrameRect(302, 51, 29, 26))

    def test_second_run_action_has_twelve_explicit_frames(self):
        self.assertEqual(len(viewer.RUN_RIGHT_ALT_FRAMES), 12)
        self.assertEqual(viewer.RUN_RIGHT_ALT_FRAMES[0].y, 80)
        self.assertEqual(viewer.RUN_RIGHT_ALT_FRAMES[-1].x, 370)

    def test_third_action_has_six_explicit_frames(self):
        self.assertEqual(len(viewer.JUMP_FRAMES), 6)
        self.assertEqual(viewer.JUMP_FRAMES[3].height, 42)
        self.assertEqual(viewer.JUMP_FRAMES[-1].x, 228)

    def test_fourth_action_has_nine_variable_size_frames(self):
        self.assertEqual(len(viewer.ACTION_4_FRAMES), 9)
        self.assertEqual(viewer.ACTION_4_FRAMES[1].height, 31)
        self.assertEqual(viewer.ACTION_4_FRAMES[-1].x, 268)

    def test_fifth_action_has_six_explicit_frames(self):
        self.assertEqual(len(viewer.ACTION_5_FRAMES), 6)
        self.assertEqual(viewer.ACTION_5_FRAMES[0].y, 206)
        self.assertEqual(viewer.ACTION_5_FRAMES[-1].x, 174)

    def test_sixth_action_has_six_explicit_frames(self):
        self.assertEqual(len(viewer.ACTION_6_FRAMES), 6)
        self.assertEqual(viewer.ACTION_6_FRAMES[3].y, 238)
        self.assertEqual(viewer.ACTION_6_FRAMES[-1].x, 186)

    def test_seventh_action_has_six_explicit_frames(self):
        self.assertEqual(len(viewer.ACTION_7_FRAMES), 6)
        self.assertEqual(viewer.ACTION_7_FRAMES[2].width, 39)
        self.assertEqual(viewer.ACTION_7_FRAMES[-1].x, 218)

    def test_eighth_action_has_eight_explicit_frames(self):
        self.assertEqual(len(viewer.ACTION_8_FRAMES), 8)
        self.assertEqual(viewer.ACTION_8_FRAMES[0].height, 45)
        self.assertEqual(viewer.ACTION_8_FRAMES[-1].x, 232)

    def test_action_catalog_preserves_sheet_order_and_frame_counts(self):
        self.assertEqual(
            [len(action.frames) for action in viewer.SONIC_ACTIONS],
            [11, 12, 6, 9, 6, 6, 6, 8],
        )
        self.assertEqual(
            [(action.direction_x, action.direction_y) for action in viewer.SONIC_ACTIONS[:2]],
            [(1, 0), (1, 0)],
        )
        self.assertEqual([action.name for action in viewer.SONIC_ACTIONS], [
            "동작 1", "동작 2", "동작 3", "동작 4",
            "동작 5", "동작 6", "동작 7", "동작 8",
        ])

    def test_all_action_rectangles_fit_the_sonic_sheet(self):
        self.assertIs(viewer.validate_actions(), viewer.SONIC_ACTIONS)
        for action in viewer.SONIC_ACTIONS:
            for frame in action.frames:
                self.assertGreater(frame.width, 0)
                self.assertGreater(frame.height, 0)
                self.assertLessEqual(frame.x + frame.width, 399)
                self.assertLessEqual(frame.y + frame.height, 525)

    def test_action_validation_rejects_out_of_bounds_rectangles(self):
        invalid_action = viewer.AnimationAction(
            "bad",
            (viewer.FrameRect(398, 0, 2, 10),),
        )
        with self.assertRaises(ValueError):
            viewer.validate_actions((invalid_action,))

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