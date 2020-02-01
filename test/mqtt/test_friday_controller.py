"""
Project:
Author:
"""
import unittest

from src.mqtt.friday_controller import FridayController


class FridayControllerTestCase(unittest.TestCase):

    def setUp(self):
        self._target = FridayController()

    def test_handler_list_correct_value(self):
        expect_handler_list_length = 2
        actual_handler_list_length = len(self._target.HANDLER_LIST)

        self.assertEqual(
            actual_handler_list_length,
            expect_handler_list_length
        )
