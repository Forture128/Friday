
import paho.mqtt.client as mqtt

from utils.object_utils import is_object_has_method
from utils.get_subscribtion import build_mapper_subscribe_handlers


class GetDataFromDevice(mqtt.Client):

    HANDLER_LIST = [
    ]

    # [START init server]
    def __init__(self, client_id="", protocol=mqtt.MQTTv311, transport="tcp"):
        super().__init__(client_id="", protocol=mqtt.MQTTv311, transport="tcp")
        self._handler_map = build_mapper_subscribe_handlers(
            self.get_handler_list())
        self.transport = transport
        self.protocol = protocol
        self.client_id = client_id
        self._hostname = ''
        self._port = 0
        self._keep_alive = 60

    def config_initialize(self, hostname, port, keep_alive):
        self._hostname = hostname
        self._port = port
        self._keep_alive = keep_alive

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

        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        if payload is not None:
            try:
                # Mapping with topic in handler.
                for handler in self._handler_map.get(msg.topic, []):
                    if is_object_has_method(handler, "handle_for"):
                        handler.handle_for(topic, payload)
            except ValueError:
                print('payload is None')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)
    # [END mqtt_config]

    def get_handler_list(self):
        return self.HANDLER_LIST
