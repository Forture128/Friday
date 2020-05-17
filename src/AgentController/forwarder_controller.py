import paho.mqtt.client as mqtt

from src.AgentController.storage.redis_stored import RedisStored
from src.AgentController.utils.parse_command_line_arg import parse_command_line_args


class ForwarderController:

    # [START init server]
    def __init__(self):
        args = parse_command_line_args()
        self._hostname = args.host_2
        self._port = args.port_2
        self._keep_alive = 60
        self._connected = False
        self._topic = ''
        self._payload = ''
        self._redis_stored = RedisStored()
        self.forwarder_client = self.override_function()
        self.finish_publish = False

    # This method update variable topic.
    def update_topic(self, args_topic):
        self._topic = args_topic
    # [END init server]

    def run(self):
        rc = self.forwarder_client.connect(self._hostname, self._port)
        if rc == 0:
            print(self._topic)
            self.publish_data(self._topic)

    # [START mqtt_config]
    def on_connect(self, mqttc, obj, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print('on_connect_2', mqtt.connack_string(rc))
            self._connected = True
        else:
            print("Bad connection Returned code=", rc)
        while self._connected:
            payload = self.get_data_from_stored(self._topic)
            self.publish_data(payload)

    def on_message(self, mqttc, obj, msg):
        print('[SendDataToGCP] on_message')
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("[SendDataToGCP] Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print('on_log [SendDataToGCP]')
        print(string)

    def on_disconnect(self, mqttc, obj, rc):
        print('on_disconnect')

    def on_publish(self, mqtt, obj, mid):
        print('Publish data successful with data of', self._topic)
        self.finish_publish = True
    # [END mqtt_config]

    # Function get data from redis by key(topic)
    def get_data_from_stored(self, topic_key):
        if topic_key:
            return self._redis_stored.get_value(topic_key)
        else:
            raise ValueError('Key is empty or None ')

    # This method override function of paho_mqtt_client
    def override_function(self):
        client = mqtt.Client("", True, None, mqtt.MQTTv31)
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.on_subscribe = self.on_subscribe
        client.on_publish = self.on_publish
        client.on_log = self.on_log
        client.on_disconnect = self.on_disconnect
        return client

    # Publish data to Forwarder-server.
    def publish_data(self, key_value):
        try:
            data = self.get_data_from_stored(key_value)
            self.forwarder_client.publish(self._topic, data)
        except Exception as e:
            print('Exception ', e)


# if __name__ == '__main__':
#     test_client = ForwarderController()
#     topic = 'esp32/dht11/humidity'
#     test_client.initialize_config_topic(topic)
#     test_client.run()
