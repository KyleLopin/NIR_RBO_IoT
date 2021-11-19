# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import sys
import threading
import time
import json

# installed libraries
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# local files
import device_codes


class aws_iot_mqtt:
    def __init__(self, proxy_options=None, topic=device_codes.topic):

        self.topic = topic

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=device_codes.endpoint,
            port=device_codes.port,
            cert_filepath=device_codes.cert,
            pri_key_filepath=device_codes.key,
            client_bootstrap=client_bootstrap,
            ca_filepath=device_codes.root_ca,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed,
            client_id=device_codes.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=proxy_options)

        print("Connecting to {} with client ID '{}'...".format(
            device_codes.endpoint, device_codes.client_id))

        self.connect_future = self.mqtt_connection.connect()

    def wait_for_connect(self):
        # .result() waits until a result is available
        self.connect_future.result()
        print("Connected!")

    def send_message(self, message):
        print("Publishing message to topic '{}': {}".format(self.topic, message))
        message_json = json.dumps(message)
        self.mqtt_connection.publish(
            topic=self.topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)

    def subscribe(self):
        # Subscribe
        print("Subscribing to topic '{}'...".format(self.topic))
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=self.topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))

    def disconnect(self):
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")

    @staticmethod
    def on_connection_interrupted(connection, error, **kwargs):
        """Callback when connection is accidentally lost"""
        print("Connection interrupted. error: {}".format(error))

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback when an interrupted connection is re-established"""
        print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)

    def on_resubscribe_complete(resubscribe_future):
        """"""
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback when the subscribed topic receives a message"""
        print("on message recieved", topic)
        print("Received message from topic '{}': {}".format(topic, payload))
        #TODO: add code here for receiving a message


if __name__ == "__main__":
    aws_iot_mqtt()
