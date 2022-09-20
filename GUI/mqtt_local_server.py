# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard files
import ast
import socket
import subprocess
import time
# installed libraries
import paho.mqtt.client as mqtt
# local files
import data_class
import mock_conn


# HIVEMQTT_SERVER = "localhost"
# HIVEMQTT_SERVER = "192.168.1.52"
MQTT_SERVER = "MQTTBroker.local"
MQTT_PATH_LISTEN = "device_number/+/data"
MQTT_USERNAME = "GUI MASTER"
MQTT_PASSWORD = "IamYourFather"


class LocalMQTTServer(mock_conn.ConnectionClass):
    def __init__(self, master, data=None):
        # mock_conn.ConnectionClass.__init__(self, master: tk.Tk, data=None)
        # if data:
        #     self.data = data
        # else:
        #     self.data = data_class.TimeStreamData()
        # self.master = master
        # self.connected = False
        self.client = mqtt.Client("MQTT Hub")
        self.client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
        self.client.on_connect = self._on_connection
        self.client.on_message = self._on_message

        self.client.connect(MQTT_SERVER, 1883, 60)
        self.client.loop_start()

    def _on_connection(self, client, userdata, flags, rc):
        print(f"MQTT connected with client {client}, data: {userdata}, flags:{flags}, rc: {rc}")
        self.connected = True
        client.subscribe(MQTT_PATH_LISTEN)

    def _on_message(self, client, userdata, msg):
        print(f"Got package: {msg.payload}| from topic: {msg.topic}")
        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'control' in msg.topic:
            print("TODO: Impliment control functions")

    def _on_disconnect(self, client, userdata, rc):
        print(f"Disconnected client: {client} with rc: {rc}")

    def publish(self, topic, message):
        print(f"publishing: {message}: to topic: {topic}")
        self.client.publish(topic, message)

    def parse_mqtt_data(self, data_packet):
        print("TODO: update graph(s)")
        # self.data.add_data(data_packet)
        # self.master.graph.update()

    def start_device(self, device):
        topic = f"device_number/{device}/control"
        self.publish(topic, '{"command": "start"}')

    def stop_device(self, device):
        topic = f"device_number/{device}/control"
        self.publish(topic, '{"command": "stop"}')



if __name__ == "__main__":
    mqtt = LocalMQTTServer(None, 1)
    while True:
        mqtt.publish("device_number/device_1/data",
                     '{"command": "start"}')
        time.sleep(3)
