"""
Project:
Author:
"""
import paho.mqtt.client as mqtt

from .utils.object_utils import is_object_has_method


class MQTTController(mqtt.Client):
    """
    Main MQTT Controller, this class acts as the subscriber to MQTT broker,
    then with each register topic will distribute the message to the
    actual handlers
    """

    HANDLER_LIST = [
    ]

    def initialize(self, hostname, port, keepalive):
        self._hostname = hostname
        self._port = port
        self._keepalive = keepalive

        self._handler_map = self.build_mapper_for_subscriptable_handlers(
            self.get_handler_list()
        )

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

        for handler in self._handler_map.get(msg.topic, []):
            if is_object_has_method(handler, "handle_for"):
                handler.handle_for(mqttc, obj, msg)

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):  # pragma: no cover
        self.connect(self._hostname, self._port, self._keepalive)
        self.subscribe("#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc

    def get_handler_list(self):
        return self.HANDLER_LIST

    def build_mapper_for_subscriptable_handlers(self, handler_list):
        """ Loop through handlers list to build mapper for easier handling message.

        For ex: with handler A for topic "ABC" and "DEF", handler B for topic
        "NULL" and "ABC", the mapper will be:
        {
            "ABC": [<obj A>, <obj B>],
            "NULL": [<obj B>],
            "DEF":  [<obj A>]
        }
        """
        result = {}

        for handler in handler_list:

            topic_list = []
            if is_object_has_method(handler, "get_subscriptions"):
                topic_list = handler.get_subscriptions()

            for topic in topic_list:
                result.setdefault(topic, [])
                result[topic].append(handler)

        return result


if __name__ == "__main__":
    mqttc = MQTTController()
    mqttc.initialize("localhost", 1883, 60)
    rc = mqttc.run()

    print("rc: " + str(rc))
