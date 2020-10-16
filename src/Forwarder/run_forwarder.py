from .forwarder.forwarder_broker import ForwarderClient
from .utils import parse_command_line_arg

if __name__ == '__main__':

    args = parse_command_line_arg.parse_command_line_args()

    hostname = str(args.host_1)
    port = args.port_1
    mqttc = ForwarderClient()
    mqttc.config_initialize(hostname, port, 60)
    rc = mqttc.run()
    print("rc: " + str(rc))
