# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import ast
import datetime
import json
import ssl
import tkinter as tk

# installed libraries
import boto3
from boto3.dynamodb.conditions import Key

import paho.mqtt.client as mqtt

# local files
import connection
import data_class
import global_params

AWS_MQTT_HOST = "a25h8mlp62407w-ats.iot.ap-southeast-1.amazonaws.com"
AWS_HQTT_PORT = 8883

CA_PATH = "certs/Amazon-root-CA-1.pem"
CERT_PATH = "certs/device.pem.crt"
KEY_PATH = "certs/private.pem.key"

DATA_TOPIC = "device_number/+/data"
CONTROL_TOPIC = "device_number/+/control"
DEVICES = ["device_1", "device_2", "device_3"]
POSITIONS = global_params.POSITIONS


class AWSConnection:
    def __init__(self, master, data=None):
        if data:
            self.data = data
        else:
            self.data = data_class.TimeStreamData()
        # self.db_conn = AWSConnectionDB(master, data)
        # self.db_conn.read_today()
        self.mqtt_conn = AWSConnectionMQTT(master, data)


class AWSConnectionMQTT(connection.ConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        connection.ConnectionClass.__init__(self, master,
                                            "AWS", data=data)
        self.client.tls_set(CA_PATH,
                            certfile=CERT_PATH,
                            keyfile=KEY_PATH,
                            cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2,
                            ciphers=None)
        print("AWS init")
        result = self.client.connect(AWS_MQTT_HOST,
                                     port=AWS_HQTT_PORT,
                                     keepalive=60)
        print(f"mqtt result={result}")
        self.client.subscribe(CONTROL_TOPIC)  # hack for now
        self.client.loop_start()


class AWSConnectionMQTT2:
    def __init__(self, master, data):
        self.master = master
        self.data = data
        self.connected = False
        self.mqttc = mqtt.Client("MQTT Client")
        self.mqttc.on_connect = self._on_connection
        self.mqttc.on_message = self._on_message

        self.mqttc.tls_set(CA_PATH,
                           certfile=CERT_PATH,
                           keyfile=KEY_PATH,
                           cert_reqs=ssl.CERT_REQUIRED,
                           tls_version=ssl.PROTOCOL_TLSv1_2,
                           ciphers=None)

        result = self.mqttc.connect(AWS_MQTT_HOST,
                                    port=AWS_HQTT_PORT,
                                    keepalive=60)
        print(f"mqtt result={result}")

        if result == 0:
            self.connected = True
            self.mqttc.subscribe(DATA_TOPIC)
            self.mqttc.subscribe(CONTROL_TOPIC)
            print("Subscribed")
            self.check_connections()
            # self.mqttc.publish("device_number/device_1/data", "OFF")
        self.mqttc.loop_start()

    def _on_connection(self, client, userdata, flags, rc):
        print("MQTT connected")
        self.connected = True

    def _on_message(self, client, userdata, msg):
        print("Got message:")
        print(msg.topic)
        print(msg.payload)

        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'control' in msg.topic:
            # AWS converts False to false and True to true, fix that here
            payload = msg.payload.decode('utf8').replace("false", "False")
            payload = payload.replace("true", "True")
            print(payload)

            # print(ast.literal_eval('{"status": "position 1", "running": False}'))
            msg_dict = ast.literal_eval(payload)
            print(f"msg dict: {msg_dict}")
            if "status" in msg_dict:
                if msg_dict["status"] in POSITIONS:
                    self.master.status_frame.position_online(msg_dict["status"],
                                                             msg_dict["running"])

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False

    def check_connections(self):
        """ Publish a message that the sensor
        will respond to check if the sensor is on """
        print("checking connections")
        for device in DEVICES:
            self.check_connection(device)

    def check_connection(self, device):
        topic = f"device_number/{device}/control"
        self.publish(topic, '{"status": "check"}')

    def start_device(self, device):
        topic = f"device_number/{device}/control"
        self.publish(topic, '{"command": "start"}')

    def stop_device(self, device):
        topic = f"device_number/{device}/control"
        self.publish(topic, '{"command": "stop"}')

    def publish(self, topic, message):
        self.mqttc.publish(topic, message)

    def parse_mqtt_data(self, data_packet):
        self.data.add_data(data_packet)
        self.master.graph.update()

    def parse_command_data(self, data_packet):
        print("FILL HERE ALSO")


class AWSConnectionDB:
    def __init__(self, master, data, dynamodb=None):
        self.master = master
        self.data = data
        print("connecting AWS database")
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb',
                                      aws_access_key_id="AKIASKWLIZDDSEEZHSOM",
                                      aws_secret_access_key="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",
                                      region_name="ap-southeast-1")

        self.info_table = dynamodb.Table('RBO_info_table')
        self.raw_table = dynamodb.Table('RBO_raw_table')

    def send_data(self, device, date, time, info_data, raw_data):
        print(raw_data)
        print(info_data)
        response = self.raw_table.put_item(
            Item={
                "Date": date,
                "Device": device,
                "time": time,
                "Data": raw_data
                })
        print(f"first response: {response}")
        if raw_data:
            response = self.info_table.put_item(
                Item={
                    "Date": date,
                    "Device": device,
                    "time": time,
                    "info": info_data
                })
            print(f"second response: {response}")

    def read_today(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        # today = "2021-10-24"
        print(today, type(today))
        today_data = self.table.query(
            KeyConditionExpression=Key("Date").eq(today)
        )

        self.parse_db_data(today_data["Items"])

    def parse_db_data(self, data_packet):
        print("parsing data")
        for data_line in data_packet:
            print(data_line)
            print(type(data_line))
            self.data.add_data(data_line)
        for device in self.data.devices:
            print(device)
            print(self.data.devices[device])
            print("updating graph", self.master)
            device_data = self.data.devices[device]
            self.master.graph.update(device, device_data.time_series,
                                     device_data.oryzanol,
                                     device_data.rolling)
