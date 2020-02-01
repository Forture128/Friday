"""
Project:
Author:
"""
import unittest
from unittest.mock import patch, call, MagicMock

from src.mqtt.mqtt_controller import MQTTController


class MQTTControllerTestCase(unittest.TestCase):

    def setUp(self):
        self._target = MQTTController()

    def test_initialize(self):
        self._target.initialize("hostname", "port", 60)

        self.assertEqual(self._target._hostname, "hostname")
        self.assertEqual(self._target._port, "port")
        self.assertEqual(self._target._keepalive, 60)
        self.assertDictEqual(self._target._handler_map, {})

    @patch("builtins.print")
    def test_on_connect_print_output(self, mocked_print):
        self._target.on_connect(None, None, None, None)
        assert mocked_print.mock_calls == [call('rc: None')]

    @patch("builtins.print")
    def test_on_publish_print_output(self, mocked_print):
        self._target.on_publish(None, None, None)
        assert mocked_print.mock_calls == [call('mid: None')]

    @patch("builtins.print")
    def test_on_subscribe_print_output(self, mocked_print):
        self._target.on_subscribe(None, None, None, None)
        assert mocked_print.mock_calls == [call('Subscribed: None None')]

    @patch("builtins.print")
    def test_on_log_print_output(self, mocked_print):
        self._target.on_log(None, None, None, "log string")
        assert mocked_print.mock_calls == [call('log string')]

    @patch("builtins.print")
    def test_on_message_print_output(self, mocked_print):
        mocked_msg = MagicMock()
        mocked_msg.topic = "topic"
        mocked_msg.qos = 0
        mocked_msg.payload = "payload"

        self._target._handler_map = {}
        self._target.on_message(None, None, mocked_msg)
        assert mocked_print.mock_calls == [call('topic 0 payload')]

    @patch("builtins.print")
    @patch("src.mqtt.utils.object_utils.is_object_has_method")
    def test_on_message_with_handler(self, mocked_has_method, _):

        mocked_has_method.return_value = True

        mocked_msg = MagicMock()
        mocked_msg.topic = "topic"
        mocked_msg.qos = 0
        mocked_msg.payload = "payload"

        mocked_handler = MagicMock()
        mocked_handler.handle_for.return_value = 0

        self._target._handler_map = {"topic": [mocked_handler]}
        self._target.on_message(None, None, mocked_msg)

        mocked_handler.handle_for.assert_called_with(None, None, mocked_msg)

    @patch("builtins.print")
    def test_on_message_with_handler_does_not_support_handle_for(self, _):  # noqa:E501

        mocked_msg = MagicMock()
        mocked_msg.topic = "topic"
        mocked_msg.qos = 0
        mocked_msg.payload = "payload"

        mocked_handler = {}

        is_show_error = False

        try:
            self._target._handler_map = {"topic": [mocked_handler]}
            self._target.on_message(None, None, mocked_msg)
        except Exception:
            is_show_error = True

        self.assertFalse(is_show_error)

    def test_build_mapper(self):
        mocked_handler = MagicMock()
        mocked_handler.get_subscriptions.return_value = ["abc", "def"]

        expect_mapper = {
            "abc": [mocked_handler],
            "def": [mocked_handler],
        }
        actual_mapper = self._target.build_mapper_for_subscriptable_handlers(
            [mocked_handler, {}]
        )
        self.assertDictEqual(actual_mapper, expect_mapper)
