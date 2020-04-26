
import paho.mqtt.client as mqtt

from utils.object_utils import is_object_has_method

RASPBERRY3_HOSTNAME = '192.168.1.115'


class GetDataFromDevice(mqtt.Client):

    HANDLER_LIST = [
    ]

    # [START init server]
    def initialize(self, hostname, port, keepalive):
        self._hostname = hostname
        self._port = port
        self._keepalive = keepalive

        self._handler_map = self.build_mapper_subscriptable_handelers(
            self.get_handler_list()
        )
    # [END init server]

    def run(self):

        self.connect(self._hostname, self._port)
        self.subscribe("#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc

    # [START mqtt_config]
    def on_connect(self, mqttc, obj, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print('on_connect', mqtt.connack_string(rc))
        else:
            print("Bad connection Returned code=", rc)

    def on_publish(self, mqttc, userdata, mid):
        """Callback when the device receives a PU-BACK."""
        print('Published message acked.')

    def on_message(self, mqttc, obj, msg):
        print("SERVER_MQTT  == " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


        # Mapping with topic in handler.
        for handler in self._handler_map.get(msg.topic, []):
            if is_object_has_method(handler, "handle_for"):
                handler.handle_for(mqttc, obj, msg)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)
    # [END mqtt_config]

    def get_handler_list(self):
        return self.HANDLER_LIST

    def build_mapper_subscriptable_handelers(self, hander_list):
        result = {}

        for handler in hander_list:

            topic_list = []
            if is_object_has_method(handler, "get_subscription"):
                topic_list = handler.get_subscription()

            for topic in topic_list:
                result.setdefault(topic, [])
                result[topic].append(handler)
        return result


if __name__ == '__main__':
    mqttc = GetDataFromDevice()
    mqttc.initialize("localhost", 1883, 60)
    rc = mqttc.run()
