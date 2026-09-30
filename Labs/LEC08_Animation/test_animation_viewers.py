import unittest
from types import SimpleNamespace
from unittest.mock import patch

import animation_viewers as viewer


class AnimationViewerTests(unittest.TestCase):
    def test_animation_state_stores_custom_animation_lists(self):
        animations = (((0, 0, 20, 30),), ((20, 0, 10, 40), (30, 0, 15, 25)))

        state = viewer.AnimationState(animations)

        self.assertIs(state.animations, animations)
        self.assertEqual(
            state.display_scale,
            viewer.calculate_animation_scale(animations),
        )
        self.assertEqual(state.action_index, 0)
        self.assertEqual(state.frame_index, 0)

    def test_animation_state_rejects_invalid_frame_lists(self):
        for animations in ((), ((),), (((1440, 0, 40, 20),),)):
            with self.subTest(animations=animations):
                with self.assertRaises(ValueError):
                    viewer.AnimationState(animations)

    def test_animation_state_accepts_custom_sprite_sheet_dimensions(self):
        animations = (((1600, 60, 100, 40),),)

        state = viewer.AnimationState(
            animations,
            sheet_width=2000,
            sheet_height=120,
        )

        self.assertIs(state.animations, animations)
        self.assertGreater(state.display_scale, 0)

    def test_repeat_count_is_configurable_with_five_as_default(self):
        animation = (((0, 0, 20, 30), (20, 0, 10, 40)),)
        self.assertEqual(viewer.AnimationState(animation).repeat_count, 5)
        state = viewer.AnimationState(animation, repeat_count=2)

        for frame_number in range(4):
            viewer.update_animation(state, frame_number * 0.11)

        self.assertEqual(state.completed_playbacks, 2)
        self.assertEqual(state.phase, viewer.PAUSING)
        with self.assertRaises(ValueError):
            viewer.AnimationState(animation, repeat_count=0)

    def test_update_uses_each_actions_frame_count(self):
        animations = (
            ((0, 0, 20, 30), (20, 0, 10, 40)),
            ((0, 40, 50, 10),),
        )
        state = viewer.AnimationState(animations)

        for frame_number in range(10):
            frame = viewer.update_animation(state, frame_number * 0.11)
            self.assertEqual(frame, (0, frame_number % 2))
            self.assertEqual(state.completed_playbacks, (frame_number + 1) // 2)

        self.assertEqual(state.phase, viewer.PAUSING)
        self.assertEqual(state.completed_playbacks, viewer.ACTION_REPEAT_COUNT)

    def test_transition_uses_next_actions_different_frame_count(self):
        animations = (
            ((0, 0, 20, 30), (20, 0, 10, 40)),
            (
                (0, 40, 50, 10),
                (0, 30, 40, 10),
                (0, 20, 30, 10),
            ),
        )
        state = viewer.AnimationState(animations)
        now = 0.0

        for _ in range(10):
            viewer.update_animation(state, now)
            now += 0.11

        self.assertEqual(state.phase, viewer.PAUSING)
        pause_end = state.pause_until
        viewer.update_animation(state, pause_end)
        self.assertEqual(state.action_index, 1)

        now = state.next_frame_time
        for frame_number in range(15):
            frame = viewer.update_animation(state, now)
            self.assertEqual(frame, (1, frame_number % 3))
            now += 0.11

        self.assertEqual(state.phase, viewer.PAUSING)
        self.assertEqual(state.completed_playbacks, viewer.ACTION_REPEAT_COUNT)

    def test_variable_length_actions_wrap_from_last_back_to_first(self):
        animations = (
            ((0, 0, 20, 30),),
            (
                (20, 0, 10, 40),
                (30, 0, 12, 28),
                (42, 0, 18, 20),
            ),
        )
        state = viewer.AnimationState(animations, repeat_count=1)

        self.assertEqual(viewer.update_animation(state, 0.0), (0, 0))
        viewer.update_animation(state, state.pause_until)
        self.assertEqual(state.action_index, 1)
        for frame_index in range(3):
            frame = viewer.update_animation(state, state.next_frame_time)
            self.assertEqual(frame, (1, frame_index))
            if frame_index < 2:
                state.next_frame_time += 0.11

        viewer.update_animation(state, state.pause_until)
        self.assertEqual(state.action_index, 0)
        self.assertEqual(state.frame_index, 0)
        self.assertEqual(state.completed_playbacks, 0)

    def test_mario_animation_data_has_five_twelve_frame_actions(self):
        self.assertEqual(len(viewer.MARIO_ANIMATIONS), 5)
        self.assertEqual(
            [len(animation) for animation in viewer.MARIO_ANIMATIONS],
            [12, 12, 12, 12, 12],
        )

    def test_trimmed_mario_frames_have_variable_source_sizes(self):
        self.assertEqual(len(viewer.MARIO_TRIMMED_ANIMATIONS), 5)
        self.assertEqual(
            [len(animation) for animation in viewer.MARIO_TRIMMED_ANIMATIONS],
            [12, 12, 12, 12, 12],
        )
        sizes = {
            (frame[2], frame[3])
            for animation in viewer.MARIO_TRIMMED_ANIMATIONS
            for frame in animation
        }

        self.assertEqual(len(sizes), 48)
        self.assertEqual(
            viewer.get_frame_rect(3, 7),
            viewer.MARIO_TRIMMED_ANIMATIONS[3][7],
        )

    def test_animation_scale_is_shared_across_different_frame_sizes(self):
        animations = (
            ((0, 0, 80, 40), (80, 0, 20, 20)),
            ((0, 40, 50, 10),),
        )
        scale = viewer.calculate_animation_scale(animations)
        large_size = viewer.calculate_display_size(80, 40, scale)
        small_size = viewer.calculate_display_size(20, 20, scale)

        self.assertEqual(large_size, (420, 210))
        self.assertEqual(small_size, (105, 105))
        self.assertLessEqual(large_size[0], viewer.MAX_DISPLAY_WIDTH)
        self.assertLessEqual(large_size[1], viewer.MAX_DISPLAY_HEIGHT)
        self.assertAlmostEqual(large_size[0] / 80, small_size[0] / 20)

    def test_animation_validation_accepts_variable_rectangles(self):
        animations = (
            ((0, 0, 20, 30), (20, 0, 15, 40)),
            ((0, 40, 50, 10),),
        )
        self.assertIs(
            viewer.validate_animations(animations, 50, 50),
            animations,
        )

    def test_animation_validation_rejects_empty_and_out_of_bounds_data(self):
        invalid_configs = (
            (),
            ((),),
            (((0, 0, 0, 10),),),
            (((49, 0, 2, 10),),),
            (((0, 0, 10),),),
        )
        for animations in invalid_configs:
            with self.subTest(animations=animations):
                with self.assertRaises(ValueError):
                    viewer.validate_animations(animations, 50, 50)

    def test_frame_lookup_returns_explicit_variable_rectangles(self):
        animations = (
            ((4, 5, 18, 33), (22, 8, 10, 30)),
            ((0, 0, 7, 9),),
        )

        self.assertEqual(viewer.get_frame_rect(0, 0, animations), (4, 5, 18, 33))
        self.assertEqual(viewer.get_frame_rect(0, 1, animations), (22, 8, 10, 30))
        self.assertEqual(viewer.get_frame_rect(1, 0, animations), (0, 0, 7, 9))
        with self.assertRaises(IndexError):
            viewer.get_frame_rect(1, 1, animations)

    def test_renderer_draws_custom_frame_rectangle_and_size(self):
        class FakeSheet:
            def __init__(self):
                self.calls = []

            def clip_draw(self, *arguments):
                self.calls.append(arguments)

        animations = (((4, 5, 18, 33), (22, 8, 10, 30)),)
        sheet = FakeSheet()
        with (
            patch.object(viewer, "clear_canvas"),
            patch.object(viewer, "update_canvas"),
        ):
            viewer.draw_action_frame(sheet, 0, 1, animations)

        self.assertEqual(sheet.calls[-1][:4], (22, 8, 10, 30))
        self.assertEqual(
            sheet.calls[-1][4:6],
            (viewer.CENTER_X, viewer.CENTER_Y),
        )
        self.assertEqual(
            sheet.calls[-1][-2:],
            viewer.calculate_display_size(
                10,
                30,
                viewer.calculate_animation_scale(animations),
            ),
        )

    def test_renderer_uses_each_mario_frame_rectangle(self):
        class FakeSheet:
            def __init__(self):
                self.last_call = None

            def clip_draw(self, *arguments):
                self.last_call = arguments

        sheet = FakeSheet()
        display_scale = viewer.calculate_animation_scale(
            viewer.MARIO_TRIMMED_ANIMATIONS
        )
        rendered_count = 0
        with (
            patch.object(viewer, "clear_canvas"),
            patch.object(viewer, "update_canvas"),
        ):
            for action_index, animation in enumerate(viewer.MARIO_TRIMMED_ANIMATIONS):
                for frame_index, rectangle in enumerate(animation):
                    viewer.draw_action_frame(sheet, action_index, frame_index)
                    self.assertEqual(sheet.last_call[:4], rectangle)
                    self.assertEqual(
                        sheet.last_call[-2:],
                        viewer.calculate_display_size(
                            rectangle[2],
                            rectangle[3],
                            display_scale,
                        ),
                    )
                    rendered_count += 1

        self.assertEqual(rendered_count, 60)

    def test_main_passes_custom_frame_lists_through_to_renderer(self):
        animations = (((5, 7, 20, 30),), ((25, 7, 10, 40), (35, 7, 12, 28)))
        sheet = object()
        events = iter([[], [SimpleNamespace(type=viewer.SDL_QUIT)]])

        with (
            patch.object(viewer, "open_canvas"),
            patch.object(viewer, "load_image", return_value=sheet),
            patch.object(viewer, "get_events", side_effect=lambda: next(events)),
            patch.object(viewer, "update_animation", return_value=(0, 0)),
            patch.object(viewer, "draw_action_frame") as draw_frame,
            patch.object(viewer, "delay"),
            patch.object(viewer, "close_canvas"),
        ):
            viewer.main(animations)

        draw_frame.assert_called_once_with(
            sheet,
            0,
            0,
            animations,
            viewer.calculate_animation_scale(animations),
        )

    def test_main_accepts_custom_sheet_path_and_dimensions(self):
        animations = (((1600, 60, 100, 40),),)
        events = iter([[SimpleNamespace(type=viewer.SDL_QUIT)]])

        with (
            patch.object(viewer, "open_canvas"),
            patch.object(viewer, "load_image", return_value=object()) as load_image,
            patch.object(viewer, "get_events", side_effect=lambda: next(events)),
            patch.object(viewer, "close_canvas"),
        ):
            viewer.main(animations, "other_sheet.png", 2000, 120)

        load_image.assert_called_once_with("other_sheet.png")

    def test_main_runs_different_frame_counts_and_wraps(self):
        animations = (
            ((0, 0, 40, 40), (40, 0, 80, 20)),
            (
                (0, 40, 60, 30),
                (60, 40, 30, 60),
                (90, 40, 50, 50),
            ),
        )
        rendered_frames = []
        wraps = [0]
        ticks = iter(index * 0.11 for index in range(200))
        original_update = viewer.update_animation

        def update_and_count_wraps(state, now):
            previous_phase = state.phase
            previous_action = state.action_index
            frame = original_update(state, now)
            if (
                previous_phase == viewer.PAUSING
                and state.phase == viewer.PLAYING
                and previous_action == 1
                and state.action_index == 0
            ):
                wraps[0] += 1
            return frame

        def events_for_one_cycle():
            if wraps[0]:
                return [SimpleNamespace(type=viewer.SDL_QUIT)]
            return []

        def record_frame(_sheet, action_index, frame_index, _animations, _scale):
            rendered_frames.append((action_index, frame_index))

        with (
            patch.object(viewer, "open_canvas"),
            patch.object(viewer, "load_image", return_value=object()),
            patch.object(viewer, "get_events", side_effect=events_for_one_cycle),
            patch.object(viewer, "monotonic", side_effect=lambda: next(ticks)),
            patch.object(viewer, "update_animation", side_effect=update_and_count_wraps),
            patch.object(viewer, "draw_action_frame", side_effect=record_frame),
            patch.object(viewer, "delay"),
            patch.object(viewer, "close_canvas") as close_canvas,
        ):
            viewer.main(animations)

        expected_frames = [(0, index % 2) for index in range(10)]
        expected_frames.extend((1, index % 3) for index in range(15))
        self.assertEqual(rendered_frames, expected_frames)
        self.assertEqual(wraps[0], 1)
        close_canvas.assert_called_once()

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

    def test_grid_builder_rejects_mismatched_or_invalid_action_data(self):
        invalid_inputs = (
            (120, 80, ((0, 30),), (2, 3)),
            (120, 80, ((0, 30),), (0,)),
            (120, 80, ((30, 30),), (2,)),
            (0, 80, ((0, 30),), (2,)),
        )
        for arguments in invalid_inputs:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    viewer.build_grid_animations(*arguments)

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