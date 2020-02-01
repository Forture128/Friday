"""
Project:
Author:
"""

from .mqtt_controller import MQTTController

from .handlers.hello_world_handler import HelloWorldHandler
from .handlers.esp32_handler import Esp32Handler


class FridayController(MQTTController):
    """ MQTT Controller with setting for Friday project """

    HANDLER_LIST = [
        HelloWorldHandler(),
        Esp32Handler(),
    ]


if __name__ == "__main__":

    import os

    hostname = os.getenv("FRIDAY_HOSTNAME", "localhost")
    port = os.getenv("FRIDAY_PORT", 1883)

    mqttc = FridayController()
    mqttc.initialize(hostname, port, 60)
    rc = mqttc.run()

    print("rc: " + str(rc))
