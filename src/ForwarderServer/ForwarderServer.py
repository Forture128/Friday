import paho.mqtt.client as mqtt

from .utils.object_utils import is_object_has_method

def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

class ForwarderServer:

    HANDLER_LIST = [
    ]

    # [START init server]
    def __init__(self):
        self._hostname = ''
        self._port = 0
        self._keep_alive = 60

    def config_initialize(self, hostname, port, keep_alive):
        self._hostname = hostname
        self._port = port
        self._keep_alive = keep_alive

    # [END init server]

    def run(self):
        forwarder_client = mqtt.Client()
        forwarder_client.on_connect = self.on_connect
        forwarder_client.on_publish = self.on_publish
        forwarder_client.on_subscribe = self.on_subscribe
        forwarder_client.on_message = self.on_message

        forwarder_client.connect(self._hostname, self._port)
        forwarder_client.subscribe("#", 0)

    # [START] Call handler
    def send_data(self,topic, payload):
        """Build mapping topic support"""
        try:
            # Mapping with topic in handler.
            for handler in self._handler_map.get(topic, []):
                if is_object_has_method(handler, "handle_for"):
                    handler.handle_for(topic, payload)
        except ValueError:
            print('payload is None')
    # [END] Call handler

    def on_connect(self, client, user_data, flags, rc):
        """Callback when connected"""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_publish(self, client, user_data, mid):
        """Callback when the device receives a PU-BACK from the MQTT bridge."""
        print('Published message.')

    def on_message(self, client, user_data, message):
        """Callback when local server receives"""

        topic = message.topic
        payload = message.payload.decode('urf-8')

        if payload is not None:
            self.send_data(topic, payload)

    def on_subscribe(self, client, user_data, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, client, user_data, level, buf):
        print(buf)

    def get_handler_list(self):
        return self.HANDLER_LIST
