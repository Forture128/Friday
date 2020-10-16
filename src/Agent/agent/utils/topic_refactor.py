"""
This class handler prepare topic base on key-redis(topic) as input.
"""
FORMAT_TELEMETRY_TOPIC = "/device/{}/events"

FORMAT_CONFIG_TOPIC = "/device/{}/config"


def get_gateway_id(topic):
    return topic.split('/')[0]


def get_device_id(topic):
    return topic.split("/")[1]


def get_topic_config(topic):
    device_id = get_device_id(topic)
    return FORMAT_CONFIG_TOPIC.format(device_id)


def get_topic_telemetry(topic):
    device_id = get_device_id(topic)
    return FORMAT_TELEMETRY_TOPIC.format(device_id)
