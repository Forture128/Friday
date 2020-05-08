import paho.mqtt.client as mqtt

from utils.parse_command_line_arg import parse_command_line_args


class ForwarderController(mqtt.Client):

    # [START init server]
    def __init__(self, client_id="", protocol=mqtt.MQTTv311, transport="tcp"):
        super().__init__(client_id="", protocol=mqtt.MQTTv311, transport="tcp")
        self.client_id = client_id
        self.transport = transport
        self.protocol = protocol
        args = parse_command_line_args()
        self._hostname = args.host_2
        self._port = args.port_2
        self._topic = ''
        self._payload = ''
        self._keep_alive = 60

    def initialize_config(self, topic, payload, keep_alive):
        self._keep_alive = keep_alive
        self._topic = topic
        self._payload = payload
    # [END init server]

    def run(self):
        self.connect(self._hostname, self._port, self._keep_alive)
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
