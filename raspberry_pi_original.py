# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"


import device_codes


#### AWS sample code ######

import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
# from uuid import uuid4
import json

# Using globals to simplify sample code
# args = parser.parse_args()

# io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

received_count = 0
received_all_event = threading.Event()



# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    # global received_count
    # received_count += 1
    # if received_count == args.count:
    #     received_all_event.set()
    # ADD THE CODE TO RECEIVE INCOMING



if __name__ == '__main__':
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    proxy_options = None
    # if (proxy_host):
    #     proxy_options = http.HttpProxyOptions(host_name=args.proxy_host, port=args.proxy_port)

    # if args.use_websocket == True:
    #     credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
    #     mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
    #         endpoint=args.endpoint,
    #         client_bootstrap=client_bootstrap,
    #         region=args.signing_region,
    #         credentials_provider=credentials_provider,
    #         http_proxy_options=proxy_options,
    #         ca_filepath=args.root_ca,
    #         on_connection_interrupted=on_connection_interrupted,
    #         on_connection_resumed=on_connection_resumed,
    #         client_id=args.client_id,
    #         clean_session=False,
    #         keep_alive_secs=30)
    #
    # else:
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=device_codes.endpoint,
        port=device_codes.port,
        cert_filepath=device_codes.cert,
        pri_key_filepath=device_codes.key,
        client_bootstrap=client_bootstrap,
        ca_filepath=device_codes.root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=device_codes.client_id,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options)

    print("Connecting to {} with client ID '{}'...".format(
        device_codes.endpoint, device_codes.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(device_codes.topics[0]))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=device_codes.topics[0],
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if device_codes.test_message:
        if device_codes.count == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(device_codes.count))

        publish_count = 1
        while (publish_count <= device_codes.count) or (device_codes.count == 0):
            message = "{} [{}]".format(device_codes.test_message, publish_count)
            print("Publishing message to topic '{}': {}".format(device_codes.topics[0], message))
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=device_codes.topics[0],
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if device_codes.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")

#### END AWS sample code ####

