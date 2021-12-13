# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"


# standard libraries
from datetime import datetime
import json
import logging
import sys
import tkinter as tk
# local files
import aws_connection
import connection
import data_class
import global_params
import graph
import info_frame
import mock_conn
import option_menu
# import mqtt_local_server

DATA_HEADERS = data_class.FILE_HEADER
today = datetime.today().strftime("%Y-%m-%d")
print(f"today: {today}")
# logging.basicConfig(filename=f'log/{today}.log',
#                     format="%(asctime)-15s %(levelname)-8s %(filename)s, %(lineno)d  %(message)s",
#                     datefmt='%m/%d/%Y %I:%M:%S %p',
#                     filemode='a+',
#                     encoding='utf-8',
#                     level=logging.INFO)


def get_settings(key):
    json_data = open("master_settings.json").read()
    json_settings = json.loads(json_data)
    return json_settings[key]

DEVICES = list(global_params.DEVICES.keys())
MOCK_DATA = get_settings("Mock input")
logging.info(f"Mocking data: {MOCK_DATA}")
MOCK_DATA = False


class RBOGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)

        self.graph = graph.TimeSeriesPlotter(self)
        print("making data in main")
        self.data = data_class.TimeStreamData(self.graph)

        # check what time stamps for each device we have recieved
        self.check_previous_data()

        # DO NOT CALL CHECK REMOTE DATA HERE,
        # takes a while for the device to respond with status
        # self.check_remote_data()

        # self.graph.add_data_class(self.data)
        self.graph.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        info = info_frame.InfoFrame(self, DEVICES)
        info.pack(side=tk.BOTTOM)
        # self.status_frame = graph.StatusFrame(self)
        # self.status_frame.pack(side=tk.BOTTOM)
        self.mqtt_broker_checkin = 0
        if MOCK_DATA:
            self.connection = mock_conn.MockConn(self, data=self.data)
            self.connection2 = mock_conn.MockConn(self, data=self.data,
                                                 name="position 3", rate=50)
        else:
            # self.connection = connection.AWSConnectionMQTT(self, self.data)
            # database = aws_connection.AWSConnectionDB(self, self.data)
            # database.read_today()
            # self.connection = mqtt_local_server.LocalMQTTServer(self, self.data)
            # self.connection = connection.LocalMQTTServer(self, self.data)
            try:
                self.connection = connection.LocalMQTTServer(self, self.data)
            except Exception as error:
                print(f"error on mqtt connection of {error}")
                self.connection = None
            # if self.connection:
            #     print("Using local MQTT server")
            # else:
            #     self.connection = connection.AWSConnectionMQTT(self, self.data)

        self.data.add_connection(self.connection)
        self.graph.add_connection(self.connection)
        menubar = option_menu.NIRMenu(self)
        self.config(menu=menubar)
        self.loop = None
        if not self.connection:
            pass
        self.maintain_mqtt_connact()

        # self.time_scale_frame = graph.TimeScale(self, self.graph)
        # self.time_scale_frame.pack(side=tk.RIGHT)

    def connect_mqtt(self):
        """
        Check for a local MQTT broker first, on the local computer
        (If this is running on the same raspberry pi with the mosquitto
        mqtt broker), next look for a local mqtt broker on the wlan
        (with the name MQTTBroker.local if the os is not named posix),
        and finally connect to the AWS MQTT server if the settings
        file indicates to
        :return: None
        """
        try:
            self.connection = connection.LocalMQTTServer(self, self.data)
        except:
            self.connection = None

    def check_mqtt(self):
        print("checking mqtt")
        if self.connection.is_server_found():
            pass

    def check_previous_data(self):
        data_filename = self.data.save_file
        print(data_filename)

        with open(data_filename, 'r') as _file:
            # use the header to find where the important information is
            header = _file.readline().split(", ")
            print(header)
            time_index = header.index("time")
            device_index = header.index("device")
            ory_index = header.index("OryConc")
            av_index = header.index("AV")
            packet_index = header.index("packet_id")
            for line in _file.readlines():
                data = line.split(",")
                device = data[device_index]
                # print(data, device)
                # make a package and send this to the add_data
                # method in the data_class.TimeStreamData
                # save_pkt = {"time": data[time_index]}
                # save_pkt["OryConc"] = float(data[ory_index])
                # save_pkt["AV"] = float(data[av_index])
                # # space in this for some reason
                # save_pkt["device"] = data[device_index].lstrip()
                # save_pkt["packet_id"] = data[packet_index]
                # # send to data_class but don't save the data again
                # # print(f"saving pkt: {save_pkt}")
                # self.data.add_data(save_pkt, save_data=False)
                try:  # incase file error just pass
                    save_pkt = {"time": data[time_index]}
                    save_pkt["OryConc"] = float(data[ory_index])
                    save_pkt["AV"] = float(data[av_index])
                    # space in this for some reason
                    save_pkt["device"] = data[device_index].lstrip()
                    save_pkt["packet_id"] = data[packet_index]
                    # send to data_class but don't save the data again
                    # print(f"saving pkt: {save_pkt}")
                    self.data.add_data(save_pkt, save_data=False)
                except Exception as error:
                    print(f"Loading data but got error: {error}")
        # for each device now go through and ask the sensor
        # if it has more data

    def check_remote_data(self, device):
        print(f"checking remote data")
        self.data.get_missing_packets(device)

    def open_file(self, filename):
        # stop reading data if opening another days data
        self.connection.stop_conn()
        # clear data
        # TODO: check this
        self.data = data_class.TimeStreamData(self.graph)

        with open(filename, 'r') as _file:
            for i, line in enumerate(_file.readlines()):
                line_split = [item.strip() for item in line.split(",")]
                # print(i, line_split)
                if i == 0:
                    time_index = line_split.index("time")
                    device_index = line_split.index("device")
                    ory_index = line_split.index("OryConc")
                    packet_id_index = line_split.index("packet_id")
                    # print(time_index, device_index, ory_index)
                else:
                    # position = line_split[device_index]
                    # device = global_params.POSITIONS[position]
                    data_pkt = {"time": line_split[time_index],
                                "device": line_split[device_index],
                                "OryConc": int(float(line_split[ory_index])),
                                "packet_id": int(line_split[packet_id_index])}
                    # print(data_pkt)
                    self.data.add_data(data_pkt, save_data=False)

    def update_model(self, device):
        self.connection.update_model(device)

    def maintain_mqtt_connact(self):
        """ Loop to keep checking if mqtt is still contacted if computer
        went to sleep"""
        self.loop = self.after(10000, self.maintain_mqtt_connact)
        # TODO: fill in
        topic = "device/hub/status"
        msg = "check"
        # print("MQTT check")
        self.mqtt_broker_checkin += 1
        if self.mqtt_broker_checkin >= 4:
            # the mqtt broker is not responding so try to restart
            self.connect_mqtt()
        self.connection.publish(topic, msg)

    def save_data(self, data_type, device):
        print(f"saving data |{data_type}| for device: {device}")
        _file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        if _file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return

        device_data = self.data.devices[device]
        if data_type == "Oryzanol":
            data_set = [device_data.oryzanol]
            _file.write(f"time, Oryzanol at {device}\n")
        elif data_type == "Temperature":
            print(f"saving temp data")
            data_set = [device_data.cpu_temp,
                        device_data.sensor_temp]
            _file.write(f"time, CPU Temp at {device}, Sensor Temp at {device}\n")
        print(device_data.time_series)
        times = device_data.time_series
        print(device_data.time_series)
        times = [i.strftime('%H:%M:%S') for i in device_data.time_series]
        for i, time in enumerate(times):
            line_items = [time]
            print(data_set)
            for item in data_set:
                print(item)
                line_items.append(str(item[i]))
            print(line_items)
            line = ",".join(line_items)
            print(line)
            _file.write(line+'\n')

    def change_scan_params(self, device, packet):
        packet["command"] = "update scan params"
        self.connection.send_command(device, packet)

    def check_sensor_settings(self, device):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        device_data = data[device]
        packet = {"command": "update signal chain"}
        packet["signal params"] = device_data

        self.connection.send_command(device, packet)
        # update the graph so the reflectance data changes
        # the graph will get the data from sensor_settings.json
        self.graph.update_signal_processing(device)

    def get_remote_data(self):
        for device in global_params.DEVICES:
            self.connection.send_command(device,
                                         {"command": "send file list"})

    def main_destroy(self):
        """
        Go through the connection and stop the mqtt loop and disconnect,
        then stop the thread in the graph to update the status labels,
        then quit, destory and exit, idk how many are actually
        needed but it works
        """
        self.after_cancel(self.loop)
        self.connection.destroy()
        self.graph.destroy()
        self.quit()
        self.destroy()
        sys.exit()


if __name__ == '__main__':
    app = RBOGUI()
    app.title("Spectrograph")
    app.geometry("1050x650")
    app.mainloop()
