# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import os
import tkinter as tk  # typehinting

# installed libraries
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# local files
import connection

load_dotenv('.env')
MQTT_USERNAME = os.getenv('HIVEMQ_USERNAME')
MQTT_PASSWORD = os.getenv('HIVEMQ_PASSWORD')
MQTT_SERVER = os.getenv('HIVEMQ_URL')

MQTT_PATH_LISTEN = "deviceHIVEMQ/+/data"
MQTT_STATUS_CHANNEL = "deviceHIVEMQ/+/status"


class HIVEMQConnection(connection.ConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        connection.ConnectionClass.__init__(self, master,
                                            "", data=data,
                                            mqtt_version=mqtt.MQTTv5)
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username=MQTT_USERNAME,
                                    password=MQTT_PASSWORD)
        self._connect()

    def _connect(self):
        print("Trying to connect to HIVEMQ Server")
        try:
            result = self.client.connect(MQTT_SERVER, 8883)
            print(f"HIVEMQ mqtt result: {result}")
        except Exception as e:
            print(f"HIVEMQ connection error: {e}")

    def _on_connection(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"HIVEMQ error on connect flag: {rc}")
            return
        print(f"MQTT connected with client {client}, data: {userdata}, flags:{flags}, rc: {rc}")
        if self._connected:
            print(f"Already connected: {self._connected}")
            return
        self._connected = True
        if not self.found_server:
            print("HIVEMQ checking connections")
            self.check_connections()
        self.found_server = True
        client.subscribe(MQTT_PATH_LISTEN, qos=2)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)

    def _on_disconnect(self, **kwargs):
        print("HIVEMQ Disconnect")
        super()._on_disconnect(**kwargs)

    def _on_subscribe(self, **kwargs):
        print("HIVEMQ Subscribe")
        super()._on_subscribe(**kwargs)

    def _on_unsubscribe(self, client, userdata, flag, rc):
        print("HIVEMQ Unsubscribe")
        client.subscribe(MQTT_PATH_LISTEN, qos=2)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)
