# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard files
import ast
from datetime import datetime
import json
import os
import ssl
import time
import tkinter as tk
import traceback
# installed libraries
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
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
# MQTT_SERVER = "192.168.1.105"
MQTT_PATH_LISTEN = "device/+/data"
MQTT_STATUS_CHANNEL = "device/+/status"
# Credentials
load_dotenv('.env')
# MQTT_USERNAME = os.getenv('MQTT_USERNAME')
# MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
# MQTT_NAME = os.getenv('MQTT_NAME')
MQTT_USERNAME = "MacDaddy"
MQTT_PASSWORD = "MacPass"
MQTT_NAME = "MacDaddy"
MQTT_VERSION = mqtt.MQTTv311

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

        if os.name != "posix":  # this is tnot the mqtt broker
            self.mqtt_server_index = 0
            self.mqtt_servers = [MQTT_SERVER]
            self.mqtt_server_index = 0
            # get all dynamic ips to test
            all_ips = os.popen('arp -a')
            for ip in all_ips:
                if 'dynamic' in ip:  # this could be the rpi mqtt broker
                    print(f"dynamic ip: {ip}")
                    print(ip.split()[0])
                    self.mqtt_servers.append(ip.split()[0])
        self.master = master
        self.loop = None
        self.found_server = False
        self._connected = False
        self.client = mqtt.Client(client_name, # clean_session=False,
                                  protocol=MQTT_VERSION)
        self.client.username_pw_set(username=MQTT_USERNAME,
                                    password=MQTT_PASSWORD)
        print(f"got client {self.client}")
        self.client.on_connect = self._on_connection
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe

    def start_conn(self):
        self.loop = self.master.after(2000, self.start_conn)
        # print(f"loop client: {self._connected}")
        if not self._connected:
            self._connect()
        self.client.loop(timeout=0.1)

    def stop_conn(self):
        self.master.after_cancel(self.loop)
        self.client.loop_stop()

    def _on_message(self, cleint, userdata, msg):
        print("Got message:", msg.topic, msg.payload)
        device = msg.topic.split("/")[1]

        # print(f"message from device: {device}")
        if "hub" not in device:
            position = global_params.DEVICES[device]
            self.master.info.check_in(position)
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

            # print(f"Got control message: {msg.payload}")
            msg_dict = ast.literal_eval(payload)
            # print(f"msg dict: {msg_dict}")
            if "status" in msg_dict:
                self.parse_mqtt_status(msg_dict)
            if 'saved files' in msg_dict:
                data_needed = check_saved_data.get_missing_data_in_files(device, msg_dict["saved files"])
                pkt = {"command": "send old data",
                       "data needed": data_needed}
                self.send_command(device, pkt)

    def parse_mqtt_status(self, packet):
        position = packet["status"]
        if position in POSITIONS:
            # print("check 1")
            if "running" in packet:
                self.master.info.position_online(position,
                                                 packet["running"])
            if "packets sent" in packet:
                # position is in the position format now
                self.data.update_latest_packet_id(position,
                                                  packet["packets sent"])
                # self.update_model(POSITIONS[position])
                # if packet["packets sent"] > 0:
                #     self.data.check_missing_packets(position, packet["packets sent"])
            if "model params" in packet:
                print("model params recieved")
                print(packet)
                # check if data from sensor is same as sent
                model_correct = self.check_model(position, packet)
                if not model_correct:
                    print("Error checking model, please reload")

    def check_model(self, position, sensor_model):
        # get the stored model
        with open("new_models.json", "r") as _file:
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
        self.publish(_topic, _message, qos=0)

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
        self.publish(_topic, _message, qos=1)

    def ask_for_stored_data(self, device, pkt_num):
        if device not in DEVICES:
            device = POSITIONS[device]
        _topic = f"device/{device}/control"
        _message = f'{{"command": "send packet", "packet numbers": {pkt_num}}}'
        self.publish(_topic, _message, qos=0)

    def parse_mqtt_data(self, packet):
        if "Raw_data" in packet:
            # update the data
            print(f"parse mqtt data keys: {packet.keys()}")
            # self.master.graph.process_raw_data(packet)
            self.data.add_data(packet)
            # the data class will update the display
        elif "data packets" in packet:
            # this is saved data packets
            for key in packet:
                print(f"data key: {key}")
                # print(f"data value: {packet[key]}")
                if "data packets" not in key:
                    # print("adding data")
                    self.data.add_data(packet[key])

    def publish(self, topic, message, qos=0):
        print(f"publishing: {message}: to topic: {topic}")
        self.client.publish(topic, message, qos=qos)

    def _on_connection(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"error on connect flag: {rc}")
            return
        print(f"MQTT connected with client {client}, data: {userdata}, flags:{flags}, rc: {rc}")
#         print(f"self connected value: {self._connected}")
        print(f"connection time: {datetime.now().strftime('%H:%M:%S')}")
        if self._connected:
            print(f"Already connected: {self._connected}")
            return
        self._connected = True
#         print(f"self connected value2: {self._connected}")

        if not self.found_server:
            print("found server ask pakcet")
            self.check_connections()
            # self.update_models()

        self.found_server = True
        client.subscribe(MQTT_PATH_LISTEN, qos=1)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)
#         self.client.loop_start()

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        print(f"Disconnected client: {client} with rc: {rc}")
        print(f"disconnection time: {datetime.now().strftime('%H:%M:%S')}")
        
    def _on_subscribe(self, client, userdata, flag, rc):
        print("Subscribed:", client, userdata, flag, rc)
        
    def _on_unsubscribe(self, client, userdata, flag, rc):
        print("unsubscribed:", client, userdata, flag, rc)
        client.subscribe(MQTT_PATH_LISTEN, qos=0)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)

    def check_connections(self):
        """ Publish a message that the sensor
        will respond to check if the sensor is on """
        print("checking connections")
        for device in DEVICES:
            print(f"check device: {device}")
            self.check_connection(device)

    def check_connection(self, device):
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"status": "check"}', qos=0)
        # the response will be picked up by the on message
        # method and that will handle the rest of updating
        # the connection status label

    def start_device(self, device):
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "start"}', qos=0)

    def stop_device(self, device):
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "stop"}', qos=0)

    def is_server_found(self):
        return self.found_server

    def update_models(self):
        for position in POSITIONS:
            self.update_model(position)

    def update_model(self, device):
        with open("new_models.json", "r") as _file:
            data = json.load(_file)
        if device not in data:
            return
        device_data = data[device]

        device_topic = f"device/{global_params.POSITIONS[device]}/control"
        update_pkt = {"command": "update model"}
        for key in device_data.keys():
            update_pkt[key] = device_data[key]
        pkt = json.dumps(update_pkt)
        self.publish(device_topic, pkt, qos=0)
        print("Done with model")

    def send_command(self, device, payload):
        device_topic = f"device/{device}/control"
        if device in global_params.POSITIONS:
            device_topic = f"device/{global_params.POSITIONS[device]}/control"
        if type(payload) is dict:
            payload = json.dumps(payload)
        self.publish(device_topic, payload, qos=0)

    def get_model_params(self, device):
        device_topic = f"device/{device}/control"
        pkt = '{"command": "send model"'
        self.publish(device_topic, pkt, qos=0)
        # the rest has to be handled in the on_message callback

    def trace_callback(self, var, index, mode):
        print(f"Trace callback variable: {self._connected.get()}")
        print(f"var: {var}, index: {index}, mode: {mode}")

    def _connect(self):
        print(f"name: {os.name}")
        if os.name == "posix":
            # raspberry pi which should be running the
            mqtt_server_name = MQTT_LOCALHOST
        else:  # mac or windows should look for external
            mqtt_server_name = self.mqtt_servers[self.mqtt_server_index]
            self.mqtt_server_index = (self.mqtt_server_index + 1) % len(self.mqtt_servers)
        print(f"connecting to: {mqtt_server_name}")
        try:
            result = self.client.connect(mqtt_server_name, 1883, 15)
            print(f"mqtt result: {result}")
            # if result == 0:
            #     self._connected = True
        except Exception as e:
            print(f"connection error: {e}")
            print(type(e))
            if 'actively refused' in str(e):
                print(f"delete the ip: {mqtt_server_name} from list")
                self.mqtt_servers.remove(mqtt_server_name)
                self.mqtt_server_index = (self.mqtt_server_index + 1) % len(self.mqtt_servers)
            self._connected = False
    
    def destroy(self):
        print("destroying connection")
        self.client.loop_stop()
        print("destroying connection2")
        self.client.disconnect()


class LocalMQTTServer(ConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        print(f"connecting with name: {MQTT_NAME}")
        ConnectionClass.__init__(self, master,
                                 MQTT_NAME, data=data)
#         self.client.username_pw_set(username=MQTT_USERNAME,
#                                     password=MQTT_PASSWORD)
        self._connect()
        # self.client.subscribe(CONTROL_TOPIC)  # hack for now

        self.start_conn()
#         self.client.loop_start()


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
