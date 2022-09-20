# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import ast
from datetime import datetime
import json
import threading
import tkinter as tk

# local files
import connection
import data_class
import global_params

POSITIONS = global_params.POSITIONS


class MSG:
    def __init__(self, data: dict, topic: str):
        self.topic = topic
        json_msg = json.dumps(data).encode()
        self.payload = json_msg


class ConnectionClass_old:
    def __init__(self, master: tk.Tk, data=None):
        if data:
            self.data = data
        else:
            self.data = data_class.TimeStreamData()
        self.master = master
        self.connected = False

    def _on_message(self, cleint, userdata, msg):
        print("Got message:")
        print(msg.topic)
        print(msg.payload)
        if 'data' in msg.topic:

            data_str = msg.payload.decode('utf8')
            # json_loaded = json.load(data_str)
            # json_data = json.dump(json_loaded, sort_keys=True)
            self.parse_mqtt_data(ast.literal_eval(data_str))
        elif 'control' in msg.topic:
            # JSON converts False to false and True to true, fix that here
            payload = msg.payload.decode('utf8').replace("false", "False")
            payload = payload.replace("true", "True")

            print("Got control message: {msg.payload}")
            msg_dict = ast.literal_eval(payload)
            print(f"msg dict: {msg_dict}")
            if "status" in msg_dict:
                if msg_dict["status"] in POSITIONS:
                    self.master.status_frame.position_online(msg_dict["status"],
                                                             msg_dict["running"])

    def parse_mqtt_data(self, packet):
        print(f"Parsing packet: {packet}")


class MockConn(connection.ConnectionClass):
    def __init__(self, master: tk.Tk, data=None,
                 name="position 2", rate=25):
        connection.ConnectionClass.__init__(self, master, "MOCK", data=data)
        self.period = 10
        self.name = name
        self.rate = rate
        self.mock_loop()

    def input_mock_data(self):
        data = self.make_mock_data()
        # print(f"Mock data: {data}")
        # make mock data package
        today = datetime.today().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        # print(type(now))
        pkt = {'date': today}
        pkt["time"] = now
        pkt["Raw_data"] = data
        pkt["device_number"] = self.name
        pkt["OryConc"] = self.period
        mock_msg = MSG(pkt, "device_number/device_2_data")
        self._on_message("", "", mock_msg)

    def make_mock_data(self):
        mock_data = []
        for i in range(301):
            mock_data.append(((i*self.rate) % self.period) + 200)
        self.period = (self.period % 900) + 60
        return mock_data

    def mock_loop(self):
        self.input_mock_data()
        self.loop_thread = self.master.after(5000, self.mock_loop)

