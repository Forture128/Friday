"""
Project:
Author:
"""

from mqtt_controller import MQTTController
from handlers.hello_world_handler import HelloWorldHandler
from handlers.esp32_handler import Esp32Handler


class FridayController(MQTTController):
    """ MQTT Controller with setting for Friday project """

    HANDLER_LIST = [
        HelloWorldHandler(),
        Esp32Handler(),
    ]


if __name__ == "__main__":
    mqttc = FridayController()
    mqttc.initialize("192.168.1.15", 1883, 60)
    rc = mqttc.run()

    print("rc: " + str(rc))
