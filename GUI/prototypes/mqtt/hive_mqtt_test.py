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
# HIVEMQTT_SERVER = 'broker.hivemq.com'

HIVEMQTT_PORT = 8883
# HIVEMQTT_PORT = 1883
# HIVEMQTT_PORT = 8000


def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))


def on_disconnect(client, userdata, rc):
    print(f'Disconnect received with rc {rc}')


print(HIVEMQTT_SERVER)
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
# client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.tls_set("isrgrootx1.pem", tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(username=HIVEMQTT_USERNAME,
                       password=HIVEMQTT_PASSWORD)
# client.connect('broker.mqttdashboard.com', 1883)
result = client.connect(HIVEMQTT_SERVER, HIVEMQTT_PORT)
print(f"result: {result}")
client.loop_forever()
