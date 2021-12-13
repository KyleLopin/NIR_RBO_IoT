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
import check_saved_data
import data_class
import global_params


DEVICES = global_params.DEVICES.keys()
POSITIONS = global_params.POSITIONS
MODEL_KEYS = ["Constant", "Coeffs", "Ref Intensities",
              "Dark Intensities"]
SETTINGS_KEYS = ["use_snv", "use_sg", "sg_window",
                 "sg_polyorder", "sg_deriv"]

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
        self.loop = None
        self.found_server = False
        self.connected = False
        self.client = mqtt.Client(client_name,
                                  protocol=mqtt.MQTTv311)
        print(f"got client {self.client}")
        self.client.on_connect = self._on_connection
        self.client.on_message = self._on_message

    def start_conn(self):
        self.loop = self.master.after(2100, self.start_conn)
        # print(f"loop client: {self.connected}")
        self.client.loop(timeout=2.0, max_packets=40)

    def stop_conn(self):
        self.master.after_cancel(self.loop)
        self.client.loop_stop()

    def _on_message(self, cleint, userdata, msg):
        print("Got message:")
        print(msg.topic)
        print(msg.payload)
        device = msg.topic.split("/")[1]
        print(f"message from device: {device}")
        if "hub" not in device:
            self.master.graph.check_in(device)
        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'hub' in msg.topic:
            # mqtt hub is still connected
            self.master.mqtt_broker_checkin = 0

        elif 'status' in msg.topic:
            # JSON converts False to false and True to true, fix that here
            payload = msg.payload.decode('utf8').replace("false", "False")
            payload = payload.replace("true", "True")

            print(f"Got control message: {msg.payload}")
            msg_dict = ast.literal_eval(payload)
            print(f"msg dict: {msg_dict}")
            if "status" in msg_dict:
                self.parse_mqtt_status(msg_dict)
            if 'saved files' in msg_dict:
                data_needed = check_saved_data.get_missing_data_in_files(device, msg_dict["saved files"])
                pkt = {"command": "send old data",
                       "data needed": data_needed}
                self.send_command(device, pkt)

    def parse_mqtt_status(self, packet):
        print("parse mqtt status ")
        print(packet["status"] == "model params")
        device = packet["status"]
        print("check 3", device in POSITIONS, device)
        if device in POSITIONS:
            print("check 1")
            if "running" in packet:
                self.master.graph.position_online(device,
                                                  packet["running"])
            if "packets sent" in packet:
                # device is in the position format now
                self.data.update_latest_packet_id(POSITIONS[device],
                                                  packet["packets sent"])
                # self.update_model(POSITIONS[device])
                if packet["packets sent"] > 0:
                    self.data.check_missing_packets(POSITIONS[device], packet["packets sent"])
                # check if all the packets the sensor read
                # have been sent to this program
                # ids_to_get = self.data.get_missing_packets(POSITIONS[device])
                # print(f"missing data: {ids_to_get}")
                # if ids_to_get:
                #     self.ask_for_remote_data(device, ids_to_get)
            print("check 2", "model params" in packet)
            if "model params" in packet:
                print("model params recieved")
                print(packet)
                # check if data from sensor is same as sent
                model_correct = self.check_model(device, packet)
                if not model_correct:
                    print("Error checking model, please reload")

    def check_model(self, position, sensor_model):
        # get the stored model
        with open("models.json", "r") as _file:
            data = json.load(_file)
        data = data[position]
        print(f"Master model params:")
        for key in MODEL_KEYS:
            print(key)
            print(data[key])
            if data[key] != sensor_model[key]:
                return False
        # if all data and sensor models are the same,
        # everything is all good, hopefully
        device = global_params.POSITIONS[position]
        print("Model correct")
        if device in self.data.devices:
            self.data.devices[device].model_checked = True
            return True
        return False  # no device

    def ask_for_model(self):
        _topic = f"device/{device}/control"
        _message = '{"command": "send model"}'
        self.publish(_topic, _message)

    def check_settings(self, position, sensor_model):
        # get the stored model
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        data = data[position]
        print(f"Master model params:")
        for key in MODEL_KEYS:
            print(key)
            print(data[key])
            if data[key] != sensor_model[key]:
                return False
        # if all data and sensor models are the same,
        # everything is all good, hopefully
        device = global_params.POSITIONS[position]
        print("Model correct")
        if device in self.data.devices:
            self.data.devices[device].model_checked = True
            return True
        return False  # no device

    def ask_for_settings(self):
        _topic = f"device/{device}/control"
        _message = '{"command": "send sensor settings"}'
        self.publish(_topic, _message)

    def ask_for_stored_data(self, device, pkt_num):
        _topic = f"device/{device}/control"
        _message = f'{{"command": "send packet", "packet numbers": {pkt_num}}}'
        self.publish(_topic, _message)

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
        if not self.found_server:
            self.check_connections()
            # self.update_models()

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

    def update_models(self):
        for position in POSITIONS:
            self.update_model(position)

    def update_model(self, device):
        with open("models.json", "r") as _file:
            data = json.load(_file)
        if device not in data:
            return
        device_data = data[device]

        device_topic = f"device/{global_params.POSITIONS[device]}/control"
        update_pkt = {"command": "update model"}
        for key in device_data.keys():
            update_pkt[key] = device_data[key]
        pkt = json.dumps(update_pkt)
        self.publish(device_topic, pkt)
        print("Done with model")

    def send_command(self, device, payload):
        device_topic = f"device/{device}/control"
        if device in global_params.POSITIONS:
            device_topic = f"device/{global_params.POSITIONS[device]}/control"
        if type(payload) is dict:
            payload = json.dumps(payload)
        self.publish(device_topic, payload)

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
                                 "GUI MQTT", data=data)
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
        # self.client.subscribe(CONTROL_TOPIC)  # hack for now

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
        # self.client.subscribe(CONTROL_TOPIC)  # hack for now
        self.start_conn()


if __name__ == "__main__":
    mqtt = LocalMQTTServer(None, 1)
    while True:
        mqtt.publish("device/device_1/data",
                     '{"command": "start"}')
        time.sleep(3)
