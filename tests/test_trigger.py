import unittest
from desky import trigger


class TriggerTest(unittest.TestCase):
    def test_something(self):
        trigger.TimeTrigger()
        self.assertEqual(True, False)
