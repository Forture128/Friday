"""
Project:
Author:
"""
import paho.mqtt.client as mqtt


class MQTTController(mqtt.Client):
    """
    Main MQTT Controller, this class acts as the subscriber to MQTT broker,
    then with each register topic will distribute the messae to the
    actual handlers
    """

    def initialize(self, hostname, port, keepalive):
        self._hostname = hostname
        self._port = port
        self._keepalive = keepalive

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self.connect(self._hostname, self._port, self._keepalive)
        self.subscribe("#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


if __name__ == "__main__":
    mqttc = MQTTController()
    mqttc.initialize("localhost", 1883, 60)
    rc = mqttc.run()

    print("rc: " + str(rc))