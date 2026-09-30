import unittest
from types import SimpleNamespace
from unittest.mock import patch

import animation_viewers as viewer


class AnimationViewerTests(unittest.TestCase):
    def test_grid_builder_supports_different_frame_counts(self):
        animations = viewer.build_grid_animations(
            120,
            80,
            ((0, 30), (30, 80)),
            (2, 3),
        )

        self.assertEqual(len(animations[0]), 2)
        self.assertEqual(len(animations[1]), 3)
        self.assertEqual(animations[0][0], (0, 50, 60, 30))
        self.assertEqual(animations[0][1], (60, 50, 60, 30))
        self.assertEqual(animations[1][2], (80, 0, 40, 50))

    def test_frame_indices_wrap(self):
        self.assertEqual(viewer.next_frame_index(10, 12), 11)
        self.assertEqual(viewer.next_frame_index(11, 12), 0)

    def test_playback_count_increments_only_after_last_frame(self):
        self.assertEqual(viewer.advance_playback_frame(0, 0, 12), (1, 0))
        self.assertEqual(viewer.advance_playback_frame(10, 0, 12), (11, 0))
        self.assertEqual(viewer.advance_playback_frame(11, 0, 12), (0, 1))

    def test_five_actions_repeat_pause_and_wrap(self):
        state = viewer.AnimationState()
        now = 0.0

        for expected_action in range(10):
            for completed_frame in range(60):
                frame = viewer.update_animation(state, now)
                expected_frame = completed_frame % viewer.FRAME_COLUMNS
                self.assertEqual(frame, (expected_action % 5, expected_frame))
                now += 0.11

            self.assertEqual(state.phase, viewer.PAUSING)
            self.assertEqual(state.completed_playbacks, viewer.ACTION_REPEAT_COUNT)
            self.assertIsNone(viewer.update_animation(state, state.pause_until - 0.001))
            self.assertEqual(state.action_index, expected_action % 5)

            pause_end = state.pause_until
            self.assertIsNone(viewer.update_animation(state, pause_end))
            self.assertEqual(state.phase, viewer.PLAYING)
            self.assertEqual(state.action_index, (expected_action + 1) % 5)
            self.assertEqual(state.frame_index, 0)
            self.assertEqual(state.completed_playbacks, 0)
            now = pause_end + 0.11

    def test_all_frame_rectangles_stay_inside_sheet(self):
        for action_index in range(len(viewer.ACTION_ROWS)):
            for frame_index in range(viewer.FRAME_COLUMNS):
                left, bottom, width, height = viewer.get_frame_rect(
                    action_index,
                    frame_index,
                )
                self.assertGreaterEqual(left, 0)
                self.assertGreaterEqual(bottom, 0)
                self.assertGreater(width, 0)
                self.assertGreater(height, 0)
                self.assertLessEqual(left + width, viewer.SHEET_WIDTH)
                self.assertLessEqual(bottom + height, viewer.SHEET_HEIGHT)

    def test_display_size_preserves_ratio_and_fits(self):
        width, height = viewer.calculate_display_size(121, 156)
        self.assertLessEqual(width, viewer.MAX_DISPLAY_WIDTH)
        self.assertLessEqual(height, viewer.MAX_DISPLAY_HEIGHT)
        self.assertAlmostEqual(width / height, 121 / 156, places=3)

    def test_quit_and_escape_events(self):
        self.assertTrue(
            viewer.should_quit([SimpleNamespace(type=viewer.SDL_QUIT)])
        )
        self.assertTrue(
            viewer.should_quit(
                [
                    SimpleNamespace(
                        type=viewer.SDL_KEYDOWN,
                        key=viewer.SDLK_ESCAPE,
                    )
                ]
            )
        )
        self.assertFalse(
            viewer.should_quit(
                [
                    SimpleNamespace(
                        type=viewer.SDL_KEYDOWN,
                        key=viewer.SDLK_a,
                    )
                ]
            )
        )

    def test_main_closes_canvas_when_quit_arrives_during_pause(self):
        events = iter(
            [
                [],
                [
                    SimpleNamespace(
                        type=viewer.SDL_KEYDOWN,
                        key=viewer.SDLK_ESCAPE,
                    )
                ],
            ]
        )
        phases_seen = []

        def enter_pause(state, _now):
            state.phase = viewer.PAUSING
            phases_seen.append(state.phase)
            return None

        with (
            patch.object(viewer, "open_canvas"),
            patch.object(viewer, "load_image", return_value=object()),
            patch.object(viewer, "get_events", side_effect=lambda: next(events)),
            patch.object(viewer, "update_animation", side_effect=enter_pause),
            patch.object(viewer, "delay"),
            patch.object(viewer, "close_canvas") as close_canvas,
        ):
            viewer.main()

        self.assertEqual(phases_seen, [viewer.PAUSING])
        close_canvas.assert_called_once()


if __name__ == "__main__":
    unittest.main()