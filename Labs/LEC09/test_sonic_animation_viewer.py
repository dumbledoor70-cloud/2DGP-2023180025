import unittest
from unittest.mock import patch

import sonic_animation_viewer as viewer


class ViewerSetupTests(unittest.TestCase):
    def test_canvas_dimensions_match_prd(self):
        self.assertEqual((viewer.CANVAS_WIDTH, viewer.CANVAS_HEIGHT), (1200, 600))

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