



import sys

from utils.object_utils import is_valid
from utils.parse_command_line_arg import parse_command_line_args

try:
    import paho.mqtt.publish as publish
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.publish"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(
        inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.publish as publish

class PublishHandler():

    def __init__(self):
        args = parse_command_line_args()
        print(args.hostname_2)
        print(args.port_2)
        self._host_name = str(args.hostname_2)
        self._port = int(args.port_2)
        self.mqtt_client = None
        self.topic = ''
        self.data = ''

    def config(self, client, topic, data):
        self.mqtt_client = client
        self.topic = topic
        self.data = data

    def run(self):
        if(is_valid(self.mqtt_client) and is_valid(self.topic) and is_valid(self.data)):
            self.mqtt_client.publish(self.topic, self.data, self._host_name, self._port)