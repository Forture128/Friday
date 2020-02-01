"""
Project:
Author:
"""
import unittest
from unittest.mock import patch, call

from src.mqtt.handlers.hello_world_handler import HelloWorldHandler


class HelloWorldHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self._target = HelloWorldHandler()

    def test_get_subscriptions_return_value(self):
        """ get_subscription should return one topic: "hello". """

        expect_subscriptions = ["hello"]
        actual_subscriptions = self._target.get_subscriptions()

        self.assertListEqual(actual_subscriptions, expect_subscriptions)

    @patch('builtins.print')
    def test_handle_for_print_output(self, mocked_print):
        """ handle_for should print "Holla!". """

        self._target.handle_for(None, None, None)
        assert mocked_print.mock_calls == [call("Holla!")]
