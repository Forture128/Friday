import paho.mqtt.client as mqtt

class ForwarderClient(mqtt.Client):

    def __init__(self):
        self._hostname = ''
        self._port = 0
        self._keep_alive = 60

    def config_initialize(self, hostname, port, keep_alive):
        self._hostname = hostname
        self._port = port
        self._keep_alive = keep_alive

    def run(self):
        self.connect(self._hostname, self._port)
        self.subscribe("#")
        self.loop_forever()

    def on_connect(self, mqttc, obj, flags, rc):
        """Call back when connected"""
        if rc == 0:
            print("on_connect", mqtt.connack_string(rc))

        else:
            print("Bad connection Returned code=", rc)

    def on_publish(self, mqttc, obj, userdata, mid):
        """Callback when the device receives"""
        print("Publish message acked.")

    def on_message(self, mqttc, obj, msg):
        print("on_message")
        topic = msg.topic
        payload = msg.payload.decode('urf-8')
        print("mqttc === ", mqttc)
        print("Type mqttc =", type(mqttc))
        print("Topic == ", topic)
        print("Type topic =", type(topic))
        print("Payload ==", payload)
        print("Type payload =", type(payload))
        # self.message_callback_add()
        # if not payload:
        #     try:

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print("[on_log]", string)

    # [END mqtt_config]
