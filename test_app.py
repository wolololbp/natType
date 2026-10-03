import random
import sys
import threading
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyautogui", types.SimpleNamespace(write=lambda *_: None, press=lambda *_: None))

import app


class DelayTests(unittest.TestCase):
    def test_code_mode_types_identifiers_faster_than_line_breaks(self) -> None:
        random.seed(7)
        text = "value = calculate(input)\n"
        delays = app.build_delays(text, app.seconds_per_char(33), app.CODE_MODE)

        identifier_delays = [delay for char, delay in zip(text, delays) if char.isalpha()]
        self.assertLess(max(identifier_delays), delays[-1])

    def test_code_mode_adds_extra_pause_for_blank_lines(self) -> None:
        with patch("app.random.uniform", side_effect=lambda low, high: low):
            single_break = app.build_code_delays("x\ny", 1.0)[1]
            blank_break = app.build_code_delays("x\n\ny", 1.0)[1]

        self.assertGreater(blank_break, single_break)

    def test_mode_dispatches_to_text_and_code_cadences(self) -> None:
        with patch("app.build_text_delays", return_value=[1.0]) as text_builder:
            self.assertEqual(app.build_delays("x", 1.0, app.TEXT_MODE), [1.0])
            text_builder.assert_called_once_with("x", 1.0)

        with patch("app.build_code_delays", return_value=[2.0]) as code_builder:
            self.assertEqual(app.build_delays("x", 1.0, app.CODE_MODE), [2.0])
            code_builder.assert_called_once_with("x", 1.0)

    def test_pausable_sleep_finishes_when_unpaused(self) -> None:
        pause_event = threading.Event()
        pause_event.set()
        app.pausable_sleep(0.001, pause_event)


if __name__ == "__main__":
    unittest.main()
