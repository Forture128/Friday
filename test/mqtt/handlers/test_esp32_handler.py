"""
Project:
Author:
"""
import unittest
from unittest.mock import patch, call

from src.mqtt.handlers.esp32_handler import Esp32Handler


class Esp32HandlerTestCase(unittest.TestCase):

    def setUp(self):
        self._target = Esp32Handler()

    def test_generate_topic_with_default_topic_format(self):
        kwargs = {
            "sensor_name": "D$23",
            "report_type": "light"
        }

        expect_topic = "esp32/D$23/light"
        actual_topic = self._target.generate_topic(**kwargs)

        self.assertEqual(actual_topic, expect_topic)

    def test_generate_topic_with_custom_base_name(self):
        kwargs = {
            "sensor_name": "D$23",
            "report_type": "light"
        }

        self._target.BASE_NAME = "my_base"

        expect_topic = "my_base/D$23/light"
        actual_topic = self._target.generate_topic(**kwargs)

        self.assertEqual(actual_topic, expect_topic)

    def test_generate_topic_with_none_kwargs_and_default_topic_format(self):
        kwargs = {
            "sensor_name": None,
            "report_type": None,
        }

        expect_topic = "esp32/None/None"
        actual_topic = self._target.generate_topic(**kwargs)

        self.assertEqual(actual_topic, expect_topic)

    def test_generate_topic_with_none_kwargs_and_custom_topic_format(self):
        kwargs = {
            "sensor_name": "@#$",
            "report_type": None,
        }

        self._target.TOPIC_FORMAT = "%(other_output)s,%(sensor_name)s"

        with self.assertRaises(KeyError) as context:
            self._target.generate_topic(**kwargs)

        self.assertTrue('other_output' in str(context.exception))

    def test_get_subscription_with_default_variable(self):
        expect_subscriptions = [
            "esp32/dht11/temperature",
            "esp32/dht11/heat",
            "esp32/dht11/humidity",
        ]
        actual_subscriptions = self._target.get_subscriptions()

        self.assertListEqual(expect_subscriptions, actual_subscriptions)

    def test_get_subscription_with_custom_support_sensor(self):
        self._target.SUPPORT_SENSOR = ["abc", "def"]
        expect_subscriptions = [
            "esp32/abc/temperature",
            "esp32/abc/heat",
            "esp32/abc/humidity",
            "esp32/def/temperature",
            "esp32/def/heat",
            "esp32/def/humidity",
        ]
        actual_subscriptions = self._target.get_subscriptions()

        self.assertListEqual(expect_subscriptions, actual_subscriptions)

    def test_get_subscription_with_custom_support_report_type(self):
        self._target.SUPPORT_REPORT_TYPE = ["abc", "def"]
        expect_subscriptions = [
            "esp32/dht11/abc",
            "esp32/dht11/def",
        ]
        actual_subscriptions = self._target.get_subscriptions()

        self.assertListEqual(expect_subscriptions, actual_subscriptions)

    @patch('builtins.print')
    def test_handle_for(self, mocked_print):
        self._target.handle_for(None, None, None)
        assert mocked_print.mock_calls == [call("Sensor Handled")]
