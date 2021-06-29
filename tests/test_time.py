import unittest
from desktop_buddy import time


class TimeParseTest(unittest.TestCase):
    def test_parse_milli_seconds_with_abbreviated_unit(self):
        parsed = time.parse_time_duration('23ms')
        self.assertEqual(23, parsed)

    def test_parse_milli_seconds_with_full_unit(self):
        parsed = time.parse_time_duration('23milliseconds')
        self.assertEqual(23, parsed)

    def test_parse_milli_seconds_with_short_unit(self):
        parsed = time.parse_time_duration('23mil')
        self.assertEqual(23, parsed)

    def test_parse_seconds_no_unit(self):
        parsed = time.parse_time_duration('23')
        self.assertEqual(23000, parsed)

    def test_parse_seconds_with_short_unit(self):
        parsed = time.parse_time_duration('23s')
        self.assertEqual(23000, parsed)

    def test_parse_seconds_full_unit(self):
        parsed = time.parse_time_duration('23seconds')
        self.assertEqual(23000, parsed)
