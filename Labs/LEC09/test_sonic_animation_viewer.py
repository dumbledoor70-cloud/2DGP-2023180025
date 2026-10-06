import unittest
from types import SimpleNamespace
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

    def test_animation_state_starts_at_first_frame_and_center(self):
        state = viewer.AnimationState()

        self.assertEqual((state.action_index, state.frame_index), (0, 0))
        self.assertEqual((state.x, state.y), (600, 300))
        self.assertEqual(state.phase, viewer.PLAYING)

    def test_frame_index_wrap_uses_each_action_frame_count(self):
        self.assertEqual(viewer.advance_frame_index(0, 2), (1, False))
        self.assertEqual(viewer.advance_frame_index(1, 2), (0, True))
        self.assertEqual(viewer.advance_frame_index(4, 6), (5, False))
        self.assertEqual(viewer.advance_frame_index(5, 6), (0, True))

    def test_update_repeats_variable_length_action_five_times_then_pauses(self):
        actions = (
            viewer.AnimationAction(
                "two frames",
                (viewer.FrameRect(0, 0, 20, 20), viewer.FrameRect(20, 0, 25, 18)),
            ),
            viewer.AnimationAction(
                "three frames",
                (
                    viewer.FrameRect(0, 20, 15, 15),
                    viewer.FrameRect(15, 20, 18, 15),
                    viewer.FrameRect(33, 20, 20, 15),
                ),
            ),
        )
        state = viewer.AnimationState(actions)

        for frame_number in range(10):
            action, frame = viewer.update_animation(state, frame_number * 0.11)
            self.assertEqual(action.name, "two frames")
            self.assertEqual(frame, actions[0].frames[frame_number % 2])

        self.assertEqual(state.completed_repeats, 5)
        self.assertEqual(state.phase, viewer.PAUSING)
        self.assertIsNone(viewer.update_animation(state, state.pause_until - 0.001))
        self.assertEqual(state.action_index, 0)
        self.assertIsNone(viewer.update_animation(state, state.pause_until))
        self.assertEqual(state.action_index, 1)
        self.assertEqual(state.frame_index, 0)
        self.assertEqual(state.phase, viewer.PLAYING)

        for frame_number in range(15):
            action, frame = viewer.update_animation(state, state.next_frame_time)
            self.assertEqual(action.name, "three frames")
            self.assertEqual(frame, actions[1].frames[frame_number % 3])
            state.next_frame_time += 0.11

        self.assertEqual(state.completed_repeats, 5)
        self.assertEqual(state.phase, viewer.PAUSING)

    def test_position_moves_by_action_direction_and_elapsed_time(self):
        actions = (
            viewer.AnimationAction("right", (viewer.FrameRect(0, 0, 20, 20),), 1, 0),
            viewer.AnimationAction("up", (viewer.FrameRect(20, 0, 20, 20),), 0, 1),
        )
        state = viewer.AnimationState(actions)

        self.assertEqual(viewer.update_position(state, 0.25), (630.0, 300.0))
        state.action_index = 1
        self.assertEqual(viewer.update_position(state, 0.5), (630.0, 360.0))
        with self.assertRaises(ValueError):
            viewer.update_position(state, -0.1)

    def test_position_stays_fixed_during_action_pause(self):
        action = viewer.AnimationAction(
            "moving",
            (viewer.FrameRect(0, 0, 20, 20),),
            direction_x=1,
        )
        state = viewer.AnimationState((action,))
        state.phase = viewer.PAUSING

        self.assertEqual(viewer.update_position(state, 1.0), (600, 300))

    def test_edge_contact_resets_center_without_resetting_animation_state(self):
        actions = (
            viewer.AnimationAction(
                "large run",
                (viewer.FrameRect(0, 0, 40, 30),),
                direction_x=1,
                direction_y=-1,
            ),
        )
        state = viewer.AnimationState(actions)
        state.x = 1190
        state.y = 5
        state.frame_index = 2
        state.completed_repeats = 3

        self.assertTrue(viewer.reset_position_at_edge(state))
        self.assertEqual((state.x, state.y), (600, 300))
        self.assertEqual(state.frame_index, 2)
        self.assertEqual(state.completed_repeats, 3)

        viewer.update_position(state, 1.0)
        self.assertEqual((state.x, state.y), (720.0, 180.0))
        self.assertFalse(viewer.reset_position_at_edge(state))

    def test_left_edge_resets_to_center_for_leftward_movement(self):
        action = viewer.AnimationAction(
            "left",
            (viewer.FrameRect(0, 0, 40, 30),),
            direction_x=-1,
        )
        state = viewer.AnimationState((action,))
        state.x = 10

        self.assertTrue(viewer.reset_position_at_edge(state))
        self.assertEqual((state.x, state.y), (600, 300))

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

    def test_ninth_action_uses_previously_unused_eight_frame_strip(self):
        self.assertEqual(len(viewer.ACTION_9_FRAMES), 8)
        self.assertEqual(viewer.ACTION_9_FRAMES[0], viewer.FrameRect(1, 379, 27, 38))
        self.assertEqual(viewer.ACTION_9_FRAMES[-1].x, 254)

    def test_tenth_action_uses_previously_unused_four_frame_strip(self):
        self.assertEqual(len(viewer.ACTION_10_FRAMES), 4)
        self.assertEqual(viewer.ACTION_10_FRAMES[0], viewer.FrameRect(6, 429, 34, 40))
        self.assertEqual(viewer.ACTION_10_FRAMES[-1].x, 125)

    def test_action_catalog_preserves_sheet_order_and_frame_counts(self):
        self.assertEqual(
            [len(action.frames) for action in viewer.SONIC_ACTIONS],
            [11, 12, 6, 9, 6, 6, 6, 8, 8, 4],
        )
        self.assertEqual(
            [(action.direction_x, action.direction_y) for action in viewer.SONIC_ACTIONS[:2]],
            [(1, 0), (-1, 0)],
        )
        self.assertEqual(
            [(action.direction_x, action.direction_y) for action in viewer.SONIC_ACTIONS],
            [(1, 0), (-1, 0)] + [(1, 0)] * 5 + [(0, 0), (1, 0), (0, 0)],
        )
        self.assertEqual([action.name for action in viewer.SONIC_ACTIONS], [
            "동작 1", "동작 2", "동작 3", "동작 4",
            "동작 5", "동작 6", "동작 7", "동작 8", "동작 9", "동작 10",
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

    def test_display_size_is_three_times_each_frame(self):
        frame = viewer.FrameRect(1, 39, 29, 39)

        self.assertEqual(viewer.get_display_size(frame), (87, 117))

    def test_draw_frame_uses_crop_scale_and_canvas_center(self):
        class FakeSpriteSheet:
            def __init__(self):
                self.calls = []

            def clip_draw(self, *arguments):
                self.calls.append(arguments)

        sprite_sheet = FakeSpriteSheet()
        frame = viewer.FrameRect(1, 39, 29, 39)
        with (
            patch.object(viewer, "clear_canvas"),
            patch.object(viewer, "update_canvas"),
        ):
            viewer.draw_frame(sprite_sheet, frame)

        self.assertEqual(sprite_sheet.calls, [(1, 447, 29, 39, 600, 300, 87, 117)])

    def test_left_moving_frame_uses_pico2d_horizontal_flip(self):
        class FakeSpriteSheet:
            def __init__(self):
                self.calls = []

            def clip_composite_draw(self, *arguments):
                self.calls.append(arguments)

        sprite_sheet = FakeSpriteSheet()
        frame = viewer.FrameRect(1, 39, 29, 39)
        with (
            patch.object(viewer, "clear_canvas"),
            patch.object(viewer, "update_canvas"),
        ):
            viewer.draw_frame(sprite_sheet, frame, flip_horizontal=True)

        self.assertEqual(
            sprite_sheet.calls,
            [(1, 447, 29, 39, 0.0, "h", 600, 300, 87, 117)],
        )

    def test_sprite_loader_uses_prd_asset_path(self):
        image = object()
        with patch.object(viewer, "load_image", return_value=image) as load_image:
            result = viewer.load_sprite_sheet()

        self.assertIs(result, image)
        load_image.assert_called_once_with("sonic-sprite.png")

    def test_quit_detection_handles_window_and_escape_events(self):
        self.assertTrue(viewer.should_quit([SimpleNamespace(type=viewer.SDL_QUIT)]))
        self.assertTrue(
            viewer.should_quit(
                [SimpleNamespace(type=viewer.SDL_KEYDOWN, key=viewer.SDLK_ESCAPE)]
            )
        )
        self.assertFalse(
            viewer.should_quit(
                [SimpleNamespace(type=viewer.SDL_KEYDOWN, key=0)]
            )
        )

    def test_main_opens_and_closes_canvas(self):
        with (
            patch.object(viewer, "open_canvas") as open_canvas,
            patch.object(viewer, "load_sprite_sheet", return_value=object()),
            patch.object(viewer, "get_events", return_value=[SimpleNamespace(type=viewer.SDL_QUIT)]),
            patch.object(viewer, "close_canvas") as close_canvas,
        ):
            viewer.main()

        open_canvas.assert_called_once_with(1200, 600)
        close_canvas.assert_called_once_with()

    def test_main_integrates_animation_movement_render_and_shutdown(self):
        action = viewer.AnimationAction(
            "right",
            (viewer.FrameRect(0, 0, 20, 20),),
            direction_x=1,
        )
        events = iter(
            [
                [],
                [],
                [SimpleNamespace(type=viewer.SDL_QUIT)],
            ]
        )
        clock = iter([0.0, 0.25])
        draw_positions = []
        states = []

        def update(state, _now):
            states.append(state)
            return action, action.frames[0]

        def draw(_sheet, _frame, center_x, center_y, flip_horizontal=False):
            draw_positions.append((center_x, center_y))

        with (
            patch.object(viewer, "open_canvas"),
            patch.object(viewer, "load_sprite_sheet", return_value=object()),
            patch.object(viewer, "get_events", side_effect=lambda: next(events)),
            patch.object(viewer, "monotonic", side_effect=lambda: next(clock)),
            patch.object(viewer, "update_animation", side_effect=update),
            patch.object(viewer, "draw_frame", side_effect=draw),
            patch.object(viewer, "delay"),
            patch.object(viewer, "close_canvas") as close_canvas,
        ):
            viewer.main((action,))

        self.assertEqual(draw_positions, [(600.0, 300.0), (630.0, 300.0)])
        self.assertIs(states[0], states[1])
        close_canvas.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()