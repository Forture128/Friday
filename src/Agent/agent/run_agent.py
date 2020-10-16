from agent_broker import AgentBroker

from handler_mqtt.eps32_handler import ESP32Handler
from utils import parse_command_line_arg


class AgentServer(AgentBroker):
    """ Server MQTT with setting for server Pi2 """

    HANDLER_LIST = [
        ESP32Handler()
    ]


if __name__ == '__main__':

    args = parse_command_line_arg.parse_command_line_args()

    hostname = str(args.host_1)
    port = args.port_1
    mqttc = AgentServer()
    mqttc.config_initialize(hostname, port, 60)
    rc = mqttc.run()
    print("rc: " + str(rc))
