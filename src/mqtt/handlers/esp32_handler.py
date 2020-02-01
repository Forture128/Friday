"""
Project:
Author:
"""


class Esp32Handler:
    """ This handler does the basic listen to hello topic"""

    BASE_NAME = "esp32"
    TOPIC_FORMAT = "%(base_name)s/%(sensor_name)s/%(report_type)s"
    SUPPORT_SENSOR = [
        "dht11",
    ]
    SUPPORT_REPORT_TYPE = [
        "temperature",
        "heat",
        "humidity",
    ]
    REPORT_TYPE_MAP = {
        "temperature": float,
        "heat": float,
        "humidity": float,
    }

    def generate_topic(self, sensor_name, report_type):
        return self.TOPIC_FORMAT % {
            "base_name": self.BASE_NAME,
            "sensor_name": sensor_name,
            "report_type": report_type
        }

    def get_subscriptions(self):
        result = []
        
        for sensor in self.SUPPORT_SENSOR:
            for report_type in self.SUPPORT_REPORT_TYPE:
                result.append(self.generate_topic(sensor, report_type))

        return result

    def handle_for(self, mqttc, obj, msg):
        print("Sensor Handled")
