# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import os

# installed libraries
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv('.env')
HIVEMQTT_USERNAME = os.getenv('HIVEMQ_USERNAME')
HIVEMQTT_PASSWORD = os.getenv('HIVEMQ_PASSWORD')
HIVEMQTT_SERVER = os.getenv('HIVEMQ_URL')

HIVEMQTT_PORT = 8883
MQTT_PATH_LISTEN = "device/+/data"
MQTT_STATUS_CHANNEL = "device/+/status"


def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))
    client.subscribe(MQTT_PATH_LISTEN, qos=1)
    client.subscribe(MQTT_STATUS_CHANNEL, qos=0)


def on_disconnect(client, userdata, rc):
    print(f'Disconnect received with rc {rc}')


def on_subscribed(client, userdata, flag, rc, properties=None):
    print(f"subscribed with rc: {rc}")


def on_message(client, userdata, msg):
    print(f"got message: {msg}")


print(HIVEMQTT_SERVER)
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribed
client.on_message = on_message
# client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.tls_set("isrgrootx1.pem", tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(username=HIVEMQTT_USERNAME,
                       password=HIVEMQTT_PASSWORD)
# client.connect('broker.mqttdashboard.com', 1883)
result = client.connect(HIVEMQTT_SERVER, HIVEMQTT_PORT)
print(f"result: {result}")
client.loop_forever()
