from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from configparser import ConfigParser
import sys

# Load the configuration file
config_parser = ConfigParser()
config_parser.read("../config.ini")
received_count = 0


class AwsService():

    # Callback when connection is accidentally lost.
    def on_connection_interrupted(self, connection, error, **kwargs):
        print("Connection interrupted. error: {}".format(error))

    # Callback when an interrupted connection is re-established
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print(f'Connection resumed. Return code: {return_code} session: {session_present}')

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()
            # Cannot synchronously wait for resubscribe result because we on the connection event loop thread,
            # evaluete result with a callback instead.
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)

    def on_resubscribe_complete(self, resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print(f'Resubscribe results: {resubscribe_results}')
        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit(f'Server rejected resubscribe to {topic}')

    # Callback when the subscribed topic receives a message
    def on_message_received(self, topic, payload, **kwargs):
        print(f"Received message from topic '{topic}': {payload}")
        global received_count
        received_count += 1

    def __init__(self, device_name):

        # Config for AWS
        self._endpoint = config_parser.get('AWSCONFIG', 'endpoint')
        self._cert = config_parser.get('AWSCONFIG', 'cert')
        self._key = config_parser.get('AWSCONFIG', 'key')
        self._client_id = device_name
        self._region = config_parser.get('AWSCONFIG', 'region')
        self._ca_file_path = config_parser.get('AWSCONFIG', 'ca_filepath')
        # self.topic = ''
        # self.msg = ''

        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self._endpoint,
            cert_filepath=self._cert,
            pri_cert_filepath=self._key,
            client_bootstrap=client_bootstrap,
            ca_filepath=self._ca_file_path,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed,
            client_id=self._client_id,
            clean_session=False,
            keep_alive_secs=6)

        print(f'Connecting to {self._endpoint} with {self.client_id}')

        connect_future = self.mqtt_connection.connect()

        # Future.result() waits until result is availiable

        connect_future.result()
        print('Connected')

    def subcribe_topic_aws(self, topic):
        try:
            print(f"Subscribing to topic {topic}")
            subscribe_future, packet_id = self.mqtt_connection.subscribe(
                topic=topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self.on_message_received
            )
            subscribe_result = subscribe_future.result()
            print("Subscribed with {}".format(str(subscribe_result['qos'])))
        except Exception as e:
            raise e

    def publish_data(self, topic, data):
        try:
            print(f"Publishing message to topic {topic}: {data}")
        except Exception as e:
            raise e

    # Subscribe
    # if self.topic:
    #     print("Subscribing to topic '{}'...".format(self.topic))
    #     subscribe_future, packet_id = self.mqtt_connection.subscribe(
    #         topic=self.topic,
    #         qos=mqtt.QoS.AT_LEAST_ONCE,
    #         callback=on_message_received)
    #
    #     subscribe_result = subscribe_future.result()
    #     print("Subscribed with {}".format(str(subscribe_result['qos'])))
    #
    #     # Publish message to server desired number of times.
    #     # This step is skipped if message is blank.
    #     # This step loops forever if count was set to 0.
    #     if args.message:
    #         if args.count == 0:
    #             print("Sending messages until program killed")
    #         else:
    #             print("Sending {} message(s)".format(args.count))
    #
    #         publish_count = 1
    #         while (publish_count <= args.count) or (args.count == 0):
    #             message = "{} [{}]".format(args.message, publish_count)
    #             print("Publishing message to topic '{}': {}".format(args.topic, message))
    #             mqtt_connection.publish(
    #                 topic=args.topic,
    #                 payload=message,
    #                 qos=mqtt.QoS.AT_LEAST_ONCE)
    #             time.sleep(1)
    #             publish_count += 1
    #
    #     # Wait for all messages to be received.
    #     # This waits forever if count was set to 0.
    #     if args.count != 0 and not received_all_event.is_set():
    #         print("Waiting for all messages to be received...")
    #
    #     received_all_event.wait()
    #     print("{} message(s) received.".format(received_count))
    #
    #     # Disconnect
    #     print("Disconnecting...")
    #     disconnect_future = mqtt_connection.disconnect()
    #     disconnect_future.result()
    #     print("Disconnected!")
