import itertools
import json

import paho.mqtt.publish as publish

from constant import REGISTRY_WORK_ROOM
from storage.stored_service import StoredService
from utils import parse_command_line_arg


class ESP32Handler:

    def __init__(self):
        args = parse_command_line_arg.parse_command_line_args()
        self.__host__ = str(args.host_2)
        self.__port__ = args.port_2
        self._list_data = None
        self.stored_service = StoredService()
        self._list_topic = []

    TOPIC_FORMAT = "%(base_name)s/%(sensor_name)s/%(report_type)s"

    REGISTRY_ID = REGISTRY_WORK_ROOM

    BASE_DEVICE_NAME = "esp32"

    SENSORS = [
        "dht11",
        "dht22"
    ]

    SENSOR_REPORT_TYPES = [
        {
            "dht11": {
                "temperature": float,
                "heat": float,
                "humidity": float
            }
        },
        {
            "dht22": {
                "temperature": float,
                "heat": float,
                "humidity": float
            }
        }
    ]

    REPORT_TYPE_MAP = {
        "temperature": float,
        "heat": float,
        "humidity": float,
    }

    # This method generate topic
    def generate_topic(self, sensor_name, report_type):
        return self.TOPIC_FORMAT % {
            "base_name": self.BASE_DEVICE_NAME,
            "sensor_name": sensor_name,
            "report_type": report_type
        }

    # This method will get subscription topic base on component Friday support
    def get_subscription(self):
        result = []

        for sensor, sensor_type in itertools.product(self.SENSORS,
                                                     self.SENSOR_REPORT_TYPES):
            for key, report_values in sensor_type.items():
                for report_value in report_values:
                    result.append(self.generate_topic(sensor, report_value))
                    self._list_topic = list(set(result))
        return self._list_topic

    # Save into Redis with key is topic
    # Write report topic in file .txt as history to debug.
    def set_value_into_database(self, key, data):
        return self.stored_service.set_value(key, data)  # Call method set.

    def __get_data_by_key_(self, device_type_id):
        data = {}
        sensor_type = device_type_id
        sensor_keys = [i for i in self._list_topic if sensor_type in i]
        for key in sensor_keys:
            key_type = key.split("/")[2]
            data[key_type] = self.stored_service.get_value(key)
        return data


    # This method will using single-publish of paho-mqtt to send data.
    def __publish_data(self, topic, data, device_type):
        print("publish_data into {}, with data : {}".format(topic, data))
        publish.single(client_id=device_type,
                       topic=topic,
                       payload=data,
                       hostname=self.__host__,
                       port=self.__port__)

    # Handle after matching topic
    # Save payload into redis with key is topic.
    def handle_for(self, topic, payload):
        if self.set_value_into_database(topic, payload):
            device_type_id = topic.split("/")[1]
            data = self.__get_data_by_key_(device_type_id)
            print("Data = ", data)
            try:
                str_data = json.dumps(data)
                self.__publish_data(topic, str_data, device_type_id)
            except Exception as error:
                raise error
        else:
            raise Exception("Can't save payload into DB")
