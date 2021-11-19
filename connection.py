# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard files
import ast
import json
import os
import ssl
import time
import tkinter as tk
# installed libraries
import paho.mqtt.client as mqtt
# local files
import data_class
import global_params


DEVICES = global_params.DEVICES.keys()
POSITIONS = global_params.POSITIONS
# MQTT_SERVER = "localhost"
# MQTT_SERVER = "192.168.1.52"
MQTT_LOCALHOST = "localhost"
MQTT_SERVER = "MQTTBroker.local"
MQTT_PATH_LISTEN = "device/+/data"
MQTT_STATUS_CHANNEL = "device/+/status"
MQTT_USERNAME = "GUI MASTER"
MQTT_PASSWORD = "IamYourFather"

AWS_MQTT_HOST = "a25h8mlp62407w-ats.iot.ap-southeast-1.amazonaws.com"
AWS_MQTT_PORT = 8883

CA_PATH = "certs/Amazon-root-CA-1.pem"
CERT_PATH = "certs/device.pem.crt"
KEY_PATH = "certs/private.pem.key"

DATA_TOPIC = "device/+/data"
CONTROL_TOPIC = "device/+/control"


class ConnectionClass:
    def __init__(self, master: tk.Tk,
                 client_name, data=None):
        if data:
            self.data = data
        else:
            print("making connection in connection.py")
            self.data = data_class.TimeStreamData(master.graph)
        self.master = master
        self.found_server = False
        self.connected = False
        self.client = mqtt.Client(client_name)
        print(f"got client {self.client}")
        self.client.on_connect = self._on_connection
        self.client.on_message = self._on_message

    def start_conn(self):
        self.client.loop_start()

    def stop_conn(self):
        self.client.loop_stop()

    def _on_message(self, cleint, userdata, msg):
        print("Got message:")
        print(msg.topic)
        print(msg.payload)
        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'status' in msg.topic:
            # JSON converts False to false and True to true, fix that here
            payload = msg.payload.decode('utf8').replace("false", "False")
            payload = payload.replace("true", "True")

            print(f"Got control message: {msg.payload}")
            msg_dict = ast.literal_eval(payload)
            print(f"msg dict: {msg_dict}")
            if "status" in msg_dict:
                self.parse_mqtt_status(msg_dict)


    def parse_mqtt_status(self, packet):
        device = packet["status"]
        if device in POSITIONS:
            self.master.graph.position_online(device,
                                              packet["running"])
            if "packets sent" in packet:
                # device is in the position format now
                self.data.update_latest_packet_id(POSITIONS[device],
                                                  msg_dict["packets sent"])
                # check if all the packets the sensor read
                # have been sent to this program
                # ids_to_get = self.data.get_missing_packets(POSITIONS[device])
                # print(f"missing data: {ids_to_get}")
                # if ids_to_get:
                #     self.ask_for_remote_data(device, ids_to_get)
            if "model params" in packet:
                print("model params recieved")
                print(packet)

    # def ask_for_remote_data(self, device, ids):
    #     if device not in DEVICES:
    #         if device in POSITIONS:
    #             device = POSITIONS[device]
    #         else:
    #             raise Exception(f"device: {device} not in list of devices")
    #     _topic = f"device/{device}/control"
    #     pkt_size = global_params.REMOTE_ASK_PKT_SIZE
    #     if len(ids) > pkt_size:
    #         pkt_to_send = ids[:pkt_size]
    #         ids = ids[pkt_size:]
    #         self.master.after(global_params.REMOTE_ASK_TIME,
    #                           lambda d=device, i=ids: self.ask_for_remote_data(d, i))
    #     else:
    #         pkt_to_send = ids
    #
    #     _message = f'{{"command": "send packet", "packet numbers": {pkt_to_send}}}'
    #     # for some reason this is called 1 extra time with an empty list
    #     if ids:
    #         self.publish(_topic, _message)

    def parse_mqtt_data(self, packet):
        # print(f"Parsing packet: {packet}")
        print(f"TODO: fix for AWS data")
        if "Raw_data" in packet:
            # update the data
            # self.master.graph.process_raw_data(packet)
            self.data.add_data(packet)
            # the data class will update the display

    def publish(self, topic, message):
        print(f"publishing: {message}: to topic: {topic}")
        self.client.publish(topic, message)

    def _on_connection(self, client, userdata, flags, rc):
        print(f"MQTT connected with client {client}, data: {userdata}, flags:{flags}, rc: {rc}")
        print("TODO: if computer went to sleep, go back and check sensors for data")
        self.connected = True
        self.found_server = True
        client.subscribe(MQTT_PATH_LISTEN)
        client.subscribe(MQTT_STATUS_CHANNEL)

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"Disconnected client: {client} with rc: {rc}")

    def check_connections(self):
        """ Publish a message that the sensor
        will respond to check if the sensor is on """
        print("checking connections")
        for device in DEVICES:
            self.check_connection(device)

    def check_connection(self, device):
        topic = f"device/{device}/control"
        self.publish(topic, '{"status": "check"}')
        # the response will be picked up by the on message
        # method and that will handle the rest of updating
        # the connection status label

    def start_device(self, device):
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "start"}')

    def stop_device(self, device):
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "stop"}')

    def is_server_found(self):
        return self.found_server

    def update_model(self, device):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        device_data = data[device]
        device_topic = f"device/{device}/control"
        update_pkt = {"command": "update model"}
        for key in device_data.keys():
            update_pkt[key] = device_data[key]
        pkt = json.dumps(update_pkt)
        self.publish(device_topic, pkt)

    def get_model_params(self, device):
        device_topic = f"device/{device}/control"
        pkt = '{"command": "send model"'
        self.publish(device_topic, pkt)
        # the rest has to be handled in the on_message callback

    def destroy(self):
        print("destroying connection")
        self.client.loop_stop()
        print("destroying connection2")
        self.client.disconnect()


class LocalMQTTServer(ConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        ConnectionClass.__init__(self, master,
                                 "MQTT Hub", data=data)
        self.client.username_pw_set(username=MQTT_USERNAME,
                                    password=MQTT_PASSWORD)
        if os.uname() == "posix":
            # raspberry pi which should be running the
            mqtt_server_name = MQTT_LOCALHOST
        else:  # mac or windows should look for external
            print(f"connecting to: {MQTT_SERVER} on mac")
            mqtt_server_name = MQTT_SERVER

        result = self.client.connect(mqtt_server_name, 1883, 60)
        print(f"mqtt result: {result}")
        self.client.subscribe(CONTROL_TOPIC)  # hack for now

        self.start_conn()


class AWSConnectionMQTT(ConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        ConnectionClass.__init__(self, master,
                                 "AWS", data=data)
        self.client.tls_set(CA_PATH,
                            certfile=CERT_PATH,
                            keyfile=KEY_PATH,
                            cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2,
                            ciphers=None)
        print("AWS init")
        result = self.client.connect(AWS_MQTT_HOST,
                                     port=AWS_MQTT_PORT,
                                     keepalive=60)
        print(f"mqtt result={result}")
        self.client.subscribe(CONTROL_TOPIC)  # hack for now
        self.start_conn()


if __name__ == "__main__":
    mqtt = LocalMQTTServer(None, 1)
    while True:
        mqtt.publish("device/device_1/data",
                     '{"command": "start"}')
        time.sleep(3)
