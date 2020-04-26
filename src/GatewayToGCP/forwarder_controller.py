import time
import sys

from utils.parse_command_line_arg import parse_command_line_args


state_device_topic = "raspberry3b/state"
try:
    import paho.mqtt.client as mqtt
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.client"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.client as mqtt


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

class Forwarder():

    def __init__(self, clientId=None):
        args = parse_command_line_args()

        self._hostname = str(args.hostname_2),
        self._port = int(args.port_2)

        self.connected = False
        self.called = False
        self.mqttc = mqtt.Client(clientId)
        self.on_message = self.on_connect
        self.on_connect = self.on_connect
        self.on_publish = self.on_publish
        self.on_subscribe = self.on_subscribe

    def config_forwarder(self, topic, data):
        self._topic = topic
        self._data = data
        if data:
            self.called = True

    def wait_for_connect(self, timeout):
        """ Waiting for the device connected """
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to Raspberry 3B')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_subscribe(self, unused_client, unused_userdata, unused_mid, granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_message(self, client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = str(message.payload)
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))
        if(payload=='started'):
            client.publish(self._topic, self)
        else:
            print('Not have response from Raspberry 3B')

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self.mqttc.connect(self._hostname, self._port)
        self.wait_for_connect(5)
        self.mqttc.subscribe(state_device_topic)
