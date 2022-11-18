# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Connection classes to connect to MQTT servers.
"""

__author__ = "Kyle Vitautus Lopin"

# standard files
import ast
from datetime import datetime
import json
import logging
import os
import time
import tkinter as tk

# installed libraries
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# local files
import check_saved_data
import data_class
import global_params
import update_sensor


DEVICES = global_params.DEVICES.keys()
POSITIONS = global_params.POSITIONS
MODEL_KEYS = ["Constant", "Coeffs", "Ref Intensities",
              "Dark Intensities"]
SETTINGS_KEYS = ["use_snv", "use_sg", "sg_window",
                 "sg_polyorder", "sg_deriv"]
logger = logging.getLogger(__name__)

MQTT_LOCALHOST = "localhost"
MQTT_SERVER = "MQTTBroker.local"
MQTT_PATH_LISTEN = "device/+/data"
MQTT_STATUS_CHANNEL = "device/+/status"
# Credentials
load_dotenv('.env')
MQTT_USERNAME = os.getenv('HIVEMQTT_USERNAME')
MQTT_PASSWORD = os.getenv('HIVEMQTT_PASSWORD')
MQTT_NAME = os.getenv('MQTT_NAME')
HIVEMQTT_USERNAME = os.getenv('HIVEMQ_USERNAME')
HIVEMQTT_PASSWORD = os.getenv('HIVEMQ_PASSWORD')
HIVEMQTT_SERVER = os.getenv('HIVEMQ_URL')

HIVEMQTT_PORT = 8883
MQTT_VERSION = mqtt.MQTTv311

DATA_TOPIC = "device/+/data"
CONTROL_TOPIC = "device/+/control"

CONNECTION_OPTIONS = ["HIVEMQ"]


class ConnectionClass:
    """
    Handle all high level MQTT communications, including make and handling
    multiple servers and their priorities of communication.
    """
    def __init__(self, root: tk.Tk, data: data_class.TimeStreamData):
        """
        Hardwired to use mosquitto as default and to fall back to HIVEMQ when
        local mosquitto MQTT is not working.

        Args:
            root (tk.Tk):  root application, needed for base communication
            data (data_class.TimeStreamData):  data class to pass received data to
        """
        # the communications can be different, but it sends the data to the same place
        if 'local' in CONNECTION_OPTIONS:
            self.local_mqtt = LocalMQTTServer(root, data)
        if "HIVEMQ" in CONNECTION_OPTIONS:
            self.hivemqtt = HIVEMQConnection(root, data)

    def ask_for_stored_data(self, position, pkt_nums):
        """
        Ask a sensor to send old data that it has saved.

        Args:
            position (str): position name, ie "position 2"
            pkt_nums (list): list of packet numbers to send

        Returns: None, the sensor will respond and the on_message
        callback will handle the rest

        """
        device = POSITIONS[position]
        _topic = f"device/{device}/control"
        _message = f'{{"command": "send packet", "packet numbers": {pkt_nums}}}'
        self.publish(_topic, _message, msg_qos=0)

    def destroy(self):
        if 'local' in CONNECTION_OPTIONS:
            print("destroying local mqtt")
            self.local_mqtt.destroy()
        if "HIVEMQ" in CONNECTION_OPTIONS:
            print("destroying HIVE mqtt")
            self.hivemqtt.destroy()

    def publish(self, topic, msg, msg_qos=0):
        if 'local' in CONNECTION_OPTIONS:
            self.local_mqtt.publish(topic, msg, msg_qos)
        if "HIVEMQ" in CONNECTION_OPTIONS:
            self.hivemqtt.publish(topic, msg, msg_qos)


class BaseConnectionClass:
    """
    This class will handle base mqtt communications.  It needs a child class to
    implement the details of the specific mqtt, i.e. password and username,
    server address
    TODO: see if self.client can be removed
    TODO: see if self.data can be bound to client and removed
    """
    def __init__(self, master: tk.Tk,
                 client_name, data=None,
                 mqtt_version=MQTT_VERSION):
        if data:
            self.data = data
        else:
            print("making connection in connection.py")
            self.data = data_class.TimeStreamData(master)
        self.master = master
        self.loop = None
        self.found_server = False
        self.connected = False
        self.client = mqtt.Client(client_name, # clean_session=False,
                                  protocol=mqtt_version)
        self.client.on_connect = self._on_connection
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe
        self.update_module = update_sensor.SensorChecker(self, self.data)

    def start_conn(self):
        """
        Start a connection and keep it looping

        Returns:  None

        """
        self.loop = self.master.after(15000, self.start_conn)
        # print(f"loop client: {self._connected}")
        if not self.connected:
            self.connect()
        self.client.loop(timeout=10)

    def stop_conn(self):
        """
        Stop the loop maintaining the MQTT connection and a Paho loop if it is
        running.  Finally, disconnect the connection.
        """
        self.master.after_cancel(self.loop)
        self.client.loop_stop()
        self.client.disconnect()

    def _on_message(self, client, userdata, msg):
        """
        Handle all incoming message from the broker
        Args:
            client:  paho MQTT Client
            userdata: data associated with the MQTT channel, None now
            msg (dict): JSON package directed from the MQTT broker, usually from
            a sensor
        """
        print("Got message:", msg.topic, msg.payload)
        device = msg.topic.split("/")[1]

        # devices, i.e. "device_2" are send in the topic, convert that
        # to position, i.e. "position 2" for the rest of this program
        if device in global_params.DEVICES:
            position = global_params.DEVICES[device]
            # update the user information frame the sensor is working
            self.master.info.check_in(position)
        else:  # the topic is not correct for a device
            return
        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'hub' in msg.topic:  #TODO: depericate this part
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
                data_needed = check_saved_data.get_data_needed(device,
                                                               msg_dict["saved files"])
                pkt = {"command": "send old data",
                       "data needed": data_needed}
                self.send_command(device, pkt)

    def parse_mqtt_status(self, packet):
        """
        This parses a mqtt packet from the status channel, with a status command
        in the packet also.  This handles status updates for:
        Update if the device is running or not
        Update the number of packets the sensor has sent
        Check if model parameters are up to date - NOT TESTED YET

        Args:
            packet (dict): JSON mqtt data packet
        """
        position = packet["status"]
        if position in POSITIONS:
            if "running" in packet:
                self.master.info.position_online(position,
                                                 packet["running"])
            if "packets sent" in packet:
                self.data.update_latest_packet_id(position,
                                                  packet["packets sent"])
            if "model params" in packet:
                # check if data from sensor is same as sent
                model_correct = self.update_module.check_model(position, packet)
                if not model_correct:
                    print("Error checking model, please reload")
                    # TODO: reload the model

    def parse_mqtt_data(self, packet):
        """
        Deal with incoming data packet(s), either a current read, or older
        saved packets that coming in a large packet
        Args:
            packet (dict): data packet(s) from sensor
        """
        if "Raw_data" in packet:  # single read that just occurred
            # update the data
            print(f"parse mqtt data keys: {packet.keys()}")
            self.data.add_data(packet)
            # the data class will update the display
        elif "data packets" in packet: # this is saved data packets
            # the packet will be in the form of "packet id number": "data", i.e.
            # "198": "25, 234, 299, ...."
            for key in packet:
                print(f"data key: {key}")
                if "data packets" not in key:
                    try:
                        self.data.add_data(packet[key])
                    except Exception as _error:
                        print(f"error processing packet: {packet}")
                        logging.error(f"Error: {_error}\nprocessing packet {packet}")

    def publish(self, topic, message, qos=0):
        """
        Publish message to the topic on the MQTT broker

        Args:
            topic (str): topic to publish to
            message (str): message to send
            qos (int): quality of service to send the message with
        """
        print(f"publishing: {message}: to topic: {topic}")
        self.client.publish(topic, message, qos=qos)

    def _on_connection(self, client, userdata, flags, result, properties=None):
        """
        Callback for when a connection is made.  Check for errors in connecting,
        if connection is good and there is already not a connection made, then
        sent the connected message_id to True, and the disconnect callback can
        toggle it back if disconnected.  Also check the found_server message_id,
        if this is the first time a server has been seen, then check for
        any missing data.  TODO: move this out of HIVEMQ till tested better.

        Args:
            client: paho client that is being used,
                    could be a client for mosquitto or HIVEMQ
            userdata (None): data bound to paho client, None for now
            flags (dict): response flags from the broker
            result (int):  connection results, 0 is successful.
                           See paho docs for all options

        """
        if result != 0:
            print(f"error on connect message_id: {result}")
            return
        print(f"MQTT connected with client {client}, data: {userdata}, "
              f"flags:{flags}, qos: {result}")
        # test if already connected.
        # This happened once so the was put in to fix it? I think
        if self.connected:
            print(f"Already connected: {self.connected}")
            return
        self.connected = True
#         print(f"self connected value2: {self._connected}")

        if not self.found_server:
            print("found server ask pakcet")
            self.check_connections()
        self.found_server = True
        client.subscribe(MQTT_PATH_LISTEN, qos=1)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)
#         self.client.loop_start()

    def _on_disconnect(self, client, userdata, rc, flag):
        """
        Disconnect handler, set _connect to false so the connection loop will
        try to reconnect.  Also print out the details of the disconnection

        Args:
            client: which client was disconnected
            userdata: data bound to the paho mqtt client, currently is None
            rc: disconnection state, 0 is success
            flag: not sure, doc say this is not here, but there is
            an error without it
        """
        self.connected = False
        print(f"Disconnected client: {client}, data: {userdata}, "
              f"rc: {rc}, flag: {flag}")

    def _on_subscribe(self, client, userdata, flag, rc, properties=None):
        print("Subscribed:", rc)

    def _on_subscribe(self, client, userdata, message_id, qos, properties=None):
        """
        When subscribing print out the information about the subscription

        Args:
            client: which client was subscribed
            userdata: data bound to the paho mqtt client, currently is None
            message_id (str?): message returned from the subscribe call
            qos: quality of service granted by the broker granted
        """
        print("Subscribed:", client, userdata, message_id, qos)

    def _on_unsubscribe(self, client, userdata, message_id, result):
        """
        When unsubscribed from a topic, print out a message and re-subscribe
        TODO: test if the arguments are right
        Args:
            client: which client was unsubscribed
            userdata: data bound to the paho mqtt client, currently is None
            message_id (str): message returned from the unsubscribe call
            result: good question, is the really an arg or not
        """
        print("unsubscribed:", client, userdata, message_id, result)
        client.subscribe(MQTT_PATH_LISTEN, qos=0)
        client.subscribe(MQTT_STATUS_CHANNEL, qos=0)

    def _on_reconnect(self):
        print("reconnecting")

    def check_connections(self):
        """ Publish a message to all the sensors
        will respond to check if the sensor is on """
        print("checking connections")
        for device in DEVICES:
            print(f"check device_number: {device}")
            self.check_connection(device)

    def check_connection(self, device):
        """
        Check if the device sent is connected by sending a status check method
        through the mqtt channel.  The response will be picked up by the
        on_message method and that will handle the rest of updating
        the connection status label.

        Args:
            device (str): the device name, "device_2" or position, "position 2"
        """
        # use to be "device_2", but some send "position 2" still
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"status": "check"}', qos=0)
        # the response will be picked up by the on message
        # method and that will handle the rest of updating
        # the connection status label

    def start_device(self, device):
        """
        Send a command to start the device
        Args:
            device (str): the device name, "device_2" or position, "position 2"
        """
        # if "position 2" sent, convert it to "device_2" for mqtt channel
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "start"}', qos=0)

    def stop_device(self, device):
        """
        Send a command to stop the device

        Args:
            device (str): the device name, "device_2" or position, "position 2"
        """
        # if "position 2" sent, convert it to "device_2" for mqtt channel
        if device not in DEVICES:
            device = POSITIONS[device]
        topic = f"device/{device}/control"
        self.publish(topic, '{"command": "stop"}', qos=0)

    def is_server_found(self):
        return self.found_server

    def send_command(self, device, payload):
        device_topic = f"device/{device}/control"
        """
        Publish to the control channel of a sensor (device), can accept
        a string or dictionary for the payload and it will be converted to
        a string to send

        Args:
            device (str): device, i.e. "device_2" to publish to
            payload (dict or str): data or message to send to the sensor
        """
        device_topic = f"device/{device}/control"
        if device in global_params.POSITIONS:
            device_topic = f"device/{global_params.POSITIONS[device]}/control"
        if type(payload) is dict:
            payload = json.dumps(payload)
        self.publish(device_topic, payload, qos=0)

    def connect(self):
        print(f"name: {os.name}")
        if os.name == "posix":
            # raspberry pi which should be running the
            mqtt_server_name = MQTT_LOCALHOST
        else:  # mac or windows should look for external
            mqtt_server_name = self.mqtt_servers[self.mqtt_server_index]
            self.mqtt_server_index = (self.mqtt_server_index + 1) % len(self.mqtt_servers)
        print(f"connecting to: {mqtt_server_name}")
        try:
            result = self.client.connect(mqtt_server_name, 1883, 60)
            print(f"mqtt result: {result}")
            if result == 0:
                print("Subscribing")
        except Exception as e:
            print(f"connection error: {e}")
            print(type(e))
            if 'actively refused' in str(e):
                print(f"delete the ip: {mqtt_server_name} from list")
                self.mqtt_servers.remove(mqtt_server_name)
                self.mqtt_server_index = (self.mqtt_server_index + 1) % len(self.mqtt_servers)
            self.connected = False

    def destroy(self):
        print("destroying connection")
        self.client.loop_stop()
        print("destroying connection2")
        self.client.disconnect()


class LocalMQTTServer(BaseConnectionClass):
    """
    Impliment a BaseConnectionClass for a mosquitto MQTT broker running on
    the local WLAN
    """
    def __init__(self, master: tk.Tk, data=None):
        print(f"connecting with name: {MQTT_NAME}")
        # BaseConnectionClass.__init__(self, master,
        #                              MQTT_NAME, data=data)
        super().__init__(master, data)
        if os.name != "posix":  # this is tnot the mqtt broker
            self.mqtt_server_index = 0
            self.mqtt_servers = [MQTT_SERVER]
            self.mqtt_server_index = 0
            # get all dynamic ips to test
            all_ips = os.popen('arp -a')
            for ip in all_ips:
                if 'dynamic' in ip:  # this could be the raspberry pi MQTT broker
                    print(f"dynamic ip: {ip}")
                    print(ip.split()[0])
                    self.mqtt_servers.append(ip.split()[0])
        self.client.username_pw_set(username=MQTT_USERNAME,
                                    password=MQTT_PASSWORD)
        self.connect()
        # self.client.subscribe(CONTROL_TOPIC)  # hack for now

        self.start_conn()
#         self.client.loop_start()


class HIVEMQConnection(BaseConnectionClass):
    def __init__(self, master: tk.Tk, data=None):
        BaseConnectionClass.__init__(self, master,
                                     "", data=data,
                                     mqtt_version=mqtt.MQTTv5)

        self.client.tls_set("isrgrootx1.pem", tls_version=mqtt.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username=HIVEMQTT_USERNAME,
                                    password=HIVEMQTT_PASSWORD)
        self.connect()
        self.client.loop_start()

    def connect(self):
        print("Trying to connect to HIVEMQ Server")
        print(HIVEMQTT_SERVER)
        try:
            result = self.client.connect(HIVEMQTT_SERVER, HIVEMQTT_PORT)
            print(f"HIVEMQ mqtt result: {result}")
        except Exception as e:
            print(f"HIVEMQ connection error: {e}")
        print("end trying to connect to HIVEMQ Server")

    # def _on_connection(self, client, userdata, flags, rc):
    def _on_connection(self, client, userdata, flags, rc, properties=None):

        print("HIVE MQ on connection")
        super()._on_connection(client, userdata, flags, rc, properties)
        # if rc != 0:
        #     print(f"HIVEMQ error on connect flag: {rc}")
        #     return
        # print(f"MQTT connected with client {client}, data: {userdata}, flags:{flags}, rc: {rc}")
        # if self.connected:
        #     print(f"Already connected: {self.connected}")
        #     return
        # self.connected = True
        # if not self.found_server:
        #     print("HIVEMQ checking connections")
        #     self.check_connections()
        # self.found_server = True
        # client.subscribe(HIVEMQTT_PATH_LISTEN, qos=2)
        # client.subscribe(HIVEMQTT_STATUS_CHANNEL, qos=0)

    def _on_disconnect(self, *args):
        print("HIVEMQ Disconnect")
        print(args)
        super(HIVEMQConnection, self)._on_disconnect(*args)

    def _on_subscribe(self, *args):
        print("HIVEMQ Subscribe", args)
        super()._on_subscribe(*args)


if __name__ == "__main__":
    mqtt = LocalMQTTServer(None, 1)
    while True:
        mqtt.publish("device/device_1/data",
                     '{"command": "start"}')
        time.sleep(3)
