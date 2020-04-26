import paho.mqtt.client as mqtt


class SendDataToGCP(mqtt.Client):

    # [START init server]
    def initialize(self, hostname, port, keepalive, topic, payload):
        self._hostname = hostname
        self._port = port
        self._keepalive = keepalive
        self._topic = topic
        self._payload = payload
    # [END init server]

    def run(self):
        self.connect(self._hostname, self._port)
        self.publish(self._topic, self._payload)


    # [START mqtt_config]
    def on_connect(self, mqttc, obj, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print('on_connect_2', mqtt.connack_string(rc))
        else:
            print("Bad connection Returned code=", rc)


    def on_message(self, mqttc, obj, msg):
        print('[SendDataToGCP] on_messsage')
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("[SendDataToGCP] Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print('[SendDataToGCP]')
        print(string)

    # [END mqtt_config]