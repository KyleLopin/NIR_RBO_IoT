# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Script to listen to traffic that is coming from the HIVEMQ broker
"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import os
import time

# installed libraries
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

MQTT_PATH_LISTEN = "device/+/data"
MQTT_STATUS_CHANNEL = "device/+/status"
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
pem_path = os.path.join(__location__, '..', 'GUI', "isrgrootx1.pem")
PEM_FILE = os.path.abspath(pem_path)
env_file = os.path.join(__location__, '..', 'GUI', '.env')
load_dotenv(env_file)
HIVEMQTT_USERNAME = os.getenv('HIVEMQ_USERNAME')
HIVEMQTT_PASSWORD = os.getenv('HIVEMQ_PASSWORD')
HIVEMQTT_SERVER = os.getenv('HIVEMQ_URL')
HIVEMQTT_PORT = 8883
MQTT_VERSION = mqtt.MQTTv5


print(HIVEMQTT_SERVER)


def on_connection(client: mqtt.Client, *args):
    print("Connected")
    client.subscribe(MQTT_PATH_LISTEN)
    client.subscribe(MQTT_STATUS_CHANNEL)


def on_subscription(*args):
    print(f"got subscription: {args}")


def on_message(client, _, msg: mqtt.MQTTMessage):
    print(f"topic: {msg.topic}")
    print(f"data: {msg.payload}")


client = mqtt.Client(protocol=MQTT_VERSION)
client.on_connect = on_connection
client.on_message = on_message
client.on_subscribe = on_subscription

client.tls_set(PEM_FILE,
               tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(username=HIVEMQTT_USERNAME,
                       password=HIVEMQTT_PASSWORD)
client.connect(HIVEMQTT_SERVER, HIVEMQTT_PORT)
client.loop_forever()
while True:
    time.sleep(10)
