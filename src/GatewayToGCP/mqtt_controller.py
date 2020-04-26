from handler_mqtt.eps32_handler import ESP32Handler
from server_mqtt import GetDataFromDevice
from utils.parse_command_line_arg import parse_command_line_args


class SeverMQTT_Pi2B(GetDataFromDevice):
    """ Server MQTT with setting for server Pi2 """

    HANDLER_LIST = [
        ESP32Handler()
    ]


if __name__ == '__main__':

    args = parse_command_line_args()

    hostname = str(args.hostname_1)
    port = args.port_1
    mqttc = SeverMQTT_Pi2B()
    mqttc.initialize(hostname, port, 60)
    mqttc.run()
