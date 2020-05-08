
# [START include library]
import argparse
import datetime
import logging
import os
import random
import ssl
import time

import jwt
import paho.mqtt.client as mqtt
# [END include library]

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.CRITICAL)

# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1

# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 32

# Whether to wait with exponential backoff before publishing.
should_backoff: bool = False

# [START create_jwt]
def create_jwt(project_id, private_key_file, algorithm):
    token = {
        # The time that token was issued at
        'iat': datetime.datetime.utcnow(),
        # The time the token expires
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        # The audience field should always be set to the GCP project id.
        'aud': project_id
    }
    # Open file using open in python and with statement
    # open(file, mode)
    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key=f.read()

    print('Creating JWT using {} from private key file {}'.format(algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)
# [END create_jwt]

# [START iot_config_mqtt]
def error_str(rc):
    """Convert a Paho-mqtt error to string for develop reading"""
    return '{}: {}'.format(rc, mqtt.error_string(rc)) #

# [START on_connect function]
def on_connect(client, userdata, flags, rc):
    """Callback after device connected"""
    print('on_connect', mqtt.connack_string(rc))

    #After a successful connect, reset back-off time and stop backing off
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1
# [END on_connect function]

def on_disconnect(client, userdata, rc):
    """Callback when a device disconnects."""
    print('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with exponenttial backoff
    global should_backoff
    should_backoff = True

def on_publish(client, userdata, mid):
    """Callback when a message is sent to the broker"""
    print('on_publish')

def on_message(client, userdata, message):
    """Callback when the device receives a message on a subscription"""
    payload = str(message.payload.decode('utf-8'))
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
        payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_cert, mqtt_bridge_hostname, mqtt_bridge_port):
    client_id = 'projects/{}/location/{}/registries/{}/devices/{}'.format(
        project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # set client username, password
    # In Google Cloud IoT Core username is ignored
    # Password field is used to transmit a JWT to authorize the device
    client.username_pw_set(
        username='unused',
        password=create_jwt(project_id, private_key_file, algorithm))

    # Enable SSL/TLS support
    client.tls_set(ca_cert=ca_cert, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Assign callback function
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Connect to the Google MQTT bridge
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic the the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/command/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client
# [END iot_config_mqtt]

def detach_device(client, device_id):
    """Detach the device from the gateway."""
    # [START iot_detach_device]
    detach_topic = '/devices/{}/detach'.format(device_id)
    print('Detaching: {}'.format(detach_topic))
    client.publish(detach_topic, '{}', qos=1)
    # [END iot_detach_device]

def attach_device(client, device_id, auth):
    """Attach the device to the gateway"""
    # [START iot_attach_device]
    attach_topic = '/devices/{}/attach'.format(device_id)
    attach_payload = '{{"authorization": "{}"}}'.format(auth)
    client.publish(attach_topic, attach_payload, qos=1)
    # [END iot_attach_device]

def listen_for_messages(
        service_account_json, projects_id, cloud_region, registry_id, device_id,
        gateway_id, num_messages, private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port, jwt_expires_minutes, duration,
        cd=None):
    """Listen for messages sent to the gateway and bound devices."""
    # [START iot_listen_for_messages]
    global minimum_backoff_time

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = jwt_expires_minutes
    # Use gateway to connect to server

    client = get_client(
        projects_id, cloud_region, registry_id, gateway_id,
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
        mqtt_bridge_port)

    attach_device(client, device_id, '')
    print('Waiting for device to attach')
    time.sleep(5)

    # The topic devices receive configuration updates on.
    device_config_topic = '/devices/{}/config'.format(device_id)
    client.subscribe(device_config_topic, qos=1)

    # The topic gateway error updates on. QoS must be 0.
    error_topic = '/devices/{}/errors'.format(gateway_id)
    client.subscribe(error_topic, qos=0)

    # Wait for about a minute for config messages.
    for i in range(1, duration):
        client.loop()
        if cd is not None:
            cd(client)

        if should_backoff:
            # If backoff time is too large, give up.
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                break

            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            time.sleep(delay)
            minimum_backoff_time *=2
            client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if(seconds_since_issue > 60 * jwt_exp_mins):
            print('Refreshing token after {}s'.format(seconds_since_issue))
            jwt_iat = datetime.datetime.utcnow()
            client.loop()
            client.disconnect()
            client = get_client(
                projects_id, cloud_region, registry_id, gateway_id,
                private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
                mqtt_bridge_port)

        time.sleep(1)

    detach_device(client, device_id)

    print('Finished.')
    # [END iot listen_for_message]

def send_data_from_bound_device(
        service_accout_json, project_id, cloud_region, registry_id, device_id,
        gateway_id, num_message, private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port, jwt_expires_minutes, payload):

    """Sends data from a gateway on behalf of a device that is bound to it."""
    # [START send_data_from_bound_device]
    global minimum_backoff_time

    # Publish device event and gateway state.
    device_topic = '/device/{}/{}'.format(device_id, 'state')
    gateway_topic = '/gateway/{}/{}'.format(gateway_id, 'state')

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = jwt_expires_minutes
    # Use gateway to connect to server
    client = get_client(
        project_id, cloud_region, registry_id, gateway_id,
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
        mqtt_bridge_port)

    attach_device(client, device_id, '')
    print('Waiting for device to attach')
    time.sleep(5)

    # Publish state to gateway topic
    gateway_state = 'Starting gateway at: {}'.format(time.time())
    print(gateway_state)
    client.publish(gateway_topic, gateway_state, qos=1)

    # Publish num_messages messages to MQTT bridge
    for i in range(1, num_message + 1):
        client.loop()

        if should_backoff:
            # If backoff time is too large, give up
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                break

            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        payload = '{}/{}-{}-payload-{}'.format(
            registry_id, gateway_id, device_id, i)

        print('Publishing message {}/{}: \'{}\' to {}'.format(
            i, num_message, payload, device_topic
        ))
        client.publish(
            device_topic, '{} : {}'.format(device_id, payload), qos=1
        )

        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print('Refreshing token after {}s').format(seconds_since_issue)
            jwt_iat = datetime.datetime.utcnow()
            client = get_client(
                project_id, cloud_region, registry_id, gateway_id,
                private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
                mqtt_bridge_port)

        time.sleep(5)

    detach_device(client, device_id)

    print('Finished.')
    # [END send_data_from_bound_device]


def mqtt_device(args):
    """Connects a device, send data, and receive data."""
    # [START iot_mqtt_run]
    global  minimum_backoff_time
    global MAXIMUM_BACKOFF_TIME

    # Publish to the events or state topic based on the the flag.
    sub_topic = 'event' if args.message_type == 'event' else 'state'

    mqtt_topic = '/devices/{}/{}'.format(args.device_id, sub_topic)

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_min = args.jwt_expires_minutes
    client = get_client(
        args.project_id, args.cloud_region, args.registry_id,
        args.device_id, args.private_key_file, args.algorithm,
        args.ca_certs, args.mqtt_bridge_hostname, args.mqtt_bridge_post)

    # Publish num_messages message to the MQTT bridge once per second.
    for i in range(1, args.num_messages + 1):
        # Progress network events.
        client.loop()

        # Wait if backoff is required
        if should_backoff:
            # If backoff time is too large, give up.
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maxium backoff time.d Giving up')
                break


            # Otherwise, wait and connect again.
            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            print('Waiting for {} before reconnecting'.format(delay))
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_post)

        payload = '{}/{}-payload-{}'.format(args.registry_id, args.device_id, i)
        print('Publising message {}/{}: \'{}\''.format(
            i, args.num_messages, payload))

        # [START iot_mqtt_jwt refresh]
        second_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if second_since_issue > 60 * jwt_exp_min:
            print('Refreshing token after {}s'.format(second_since_issue))
            jwt_iat = datetime.datetime.utcnow()
            client.loop()
            client.disconnect()
            client = get_client(
                args.project_id, args.cloud_region,
                args.registry_id, args.device_id, args.private_key_file,
                args.algorithm, args.ca_certs, args.mqtt_bridge_hostname,
                args.mqtt_bridge_port)
        # [END iot_mqtt_jwt refresh]
        # Publish "payload" to MQTT topic. qos=1 means at least once
        # delivery. Cloud IoT Core also supports qos=0 for at most once
        # delivery
        client.publish(mqtt_topic, payload, qos=1)

        # Send events every second. State should not be updated as often
        for i in range(0, 60):
            time.sleep(1)
            client.loop()
    # [END iot_mqtt_run]



def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=(
            'Example Google Cloud IoT Core MQTT device connection code.'))
    parser.add_argument(
            '--algorithm',
            choices=('RS256', 'ES256'),
            required=True,
            help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
            '--ca_certs',
            default='roots.pem',
            help='CA root from https://pki.google.com/roots.pem')
    parser.add_argument(
            '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
            '--data',
            default='Hello there',
            help='The telemetry data sent on behalf of a device')
    parser.add_argument(
            '--device_id', required=True, help='Cloud IoT Core device id')
    parser.add_argument(
            '--gateway_id', required=False, help='Gateway identifier.')
    parser.add_argument(
            '--jwt_expires_minutes',
            default=20,
            type=int,
            help='Expiration time, in minutes, for JWT tokens.')
    parser.add_argument(
            '--listen_dur',
            default=60,
            type=int,
            help='Duration (seconds) to listen for configuration messages')
    parser.add_argument(
            '--message_type',
            choices=('event', 'state'),
            default='event',
            help=('Indicates whether the message to be published is a '
                  'telemetry event or a device state message.'))
    parser.add_argument(
            '--mqtt_bridge_hostname',
            default='mqtt.googleapis.com',
            help='MQTT bridge hostname.')
    parser.add_argument(
            '--mqtt_bridge_port',
            choices=(8883, 443),
            default=8883,
            type=int,
            help='MQTT bridge port.')
    parser.add_argument(
            '--num_messages',
            type=int,
            default=100,
            help='Number of messages to publish.')
    parser.add_argument(
            '--private_key_file',
            required=True,
            help='Path to private key file.')
    parser.add_argument(
            '--project_id',
            default=os.environ.get('GOOGLE_CLOUD_PROJECT'),
            help='GCP cloud project name')
    parser.add_argument(
            '--registry_id', required=True, help='Cloud IoT Core registry id')
    parser.add_argument(
            '--service_account_json',
            default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            help='Path to service account json file.')

    # Command subparser
    command = parser.add_subparsers(dest='command')

    command.add_parser(
        'device_demo',
        help=mqtt_device.__doc__)

    command.add_parser(
        'gateway_send',
        help=send_data_from_bound_device.__doc__)

    command.add_parser(
        'gateway_listen',
        help=listen_for_messages.__doc__)

    return parser.parse_args()

def main():
    args = parse_command_line_args()

    if args.command.startswith('gateway'):
        if(args.gateway_id is None):
            print('Error: For gateway commands you must specify a gateway ID')
            return

    if args.command == 'gateway_listen':
        listen_for_messages(
            args.service_account_json, args.project_id,
            args.cloud_region, args.registry_id, args.device_id,
            args.gateway_id, args.num_messages, args.private_key_file,
            args.algorithm, args.ca_certs, args.mqtt_bridge_hostname,
            args.mqtt_bridge_port, args.jwt_expires_minutes,
            args.listen_dur)
        return
    elif args.comand == 'gateway_send':
        send_data_from_bound_device(
            args.service_account_json, args.project_id,
            args.cloud_region, args.registry_id, args.device_id,
            args.gateway_id, args.num_messages, args.private_key_file,
            args.algorithm, args.ca_certs, args.mqtt_bridge_hostname,
            args.mqtt_bridge_port, args.jwt_expires_minutes, args.data)
        return
    else:
        mqtt_device(args)
    print('Finished.')


if __name__ == '__main__':
    main()


























