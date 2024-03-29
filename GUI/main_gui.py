# Copyright (c) 2022-3 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Entry point for the GUI to observe the Acid value (AV) and Oryzanol
values measured by 3 sensors in a Rice Bran Factory.  The sensors will send
a message through MQTT with the measured values
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from datetime import datetime
import json
import logging
import os
import sys
from tkinter import Tk, TOP, BOTH, BOTTOM, filedialog

# local files
import connection
import data_class
import global_params
import info_frame
import notebook
import mock_conn
import option_menu
import saved_files_funcs


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

DATA_HEADERS = data_class.SAVED_DATA_KEYS


logger = logging.getLogger('my_logger')
# will be called when main is called directly,
# not when a test is run, they will have their own log files
if not logger.hasHandlers():
    print("setting up logger")
    today = datetime.today().strftime("%Y-%m-%d")
    # log_handler = logging.FileHandler(f'log/{today}.log')
    # log_handler.setLevel(logging.DEBUG)
    # log_handler.setFormatter("%(asctime)s %(levelname)s %(filename)s %(lineno)d  %(message)s")
    # logger.addHandler(log_handler)
    test_log_handler = logging.FileHandler(f'log/{today}.log')
    test_log_handler.setLevel(logging.DEBUG)
    format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - line: %(lineno)d - %(message)s')
    test_log_handler.setFormatter(format)
    logger.addHandler(test_log_handler)
logger.debug("Start of main_gui")
print("import main")
# logging.basicConfig(filename=f'log/{today}.log',
#                     format="%(asctime)-15s %(levelname)-8s %(filename)s, %(lineno)d  %(message)s",
#                     # datefmt='%m/%d/%Y %I:%M:%S %p',
#                     filemode='a+',
#                     level=logging.DEBUG)


def get_settings(key):
    with open(os.path.join(__location__, "master_settings.json")) as _file:
        json_data = _file.read()
    json_settings = json.loads(json_data)
    return json_settings[key]


DEVICES = list(global_params.DEVICES.keys())
POSITIONS = global_params.POSITIONS
MOCK_DATA = get_settings("Mock input")
logger.info(f"Mocking data: {MOCK_DATA}")
MOCK_DATA = False


# restart the mosquitto broker to see if it helps
# connection on startup
# os.system("sudo service mosquitto stop")
# os.system("xterm -hold -e 'mosquitto -v'")


class RBOGUI(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.graphs = notebook.Notebook(self)
        self.graphs.pack(expand=True)
        print("making data in main")
        self.data = data_class.TimeStreamData(self)

        # check what time stamps for each device_number we have received
        self.load_previous_data()
        self.graphs.pack(side=TOP, expand=True, fill=BOTH)
        self.info = info_frame.InfoFrame(self, POSITIONS)
        self.info.pack(side=BOTTOM)
        # self.status_frame = graph.StatusFrame(self)
        # self.status_frame.pack(side=tk.BOTTOM)
        self.mqtt_broker_checkin = 0
        if MOCK_DATA:
            self.connection = mock_conn.MockConn(self, data=self.data)
            self.connection2 = mock_conn.MockConn(self, data=self.data,
                                                  name="position 3", rate=50)
        else:
            # print(f"root dir {dir(self)}")
            self.connection = connection.ConnectionClass(self, self.data)
        self.data.add_connection(self.connection)
        self.info.add_connection(self.connection)
        menubar = option_menu.NIRMenu(self)
        self.config(menu=menubar)
        self.loop = None
        if not self.connection:
            pass
        # self.maintain_mqtt_connact()

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
            print("connecting mqtt")
            if self.connection:
                self.connection.destroy()
            self.connection = connection.ConnectionClass(self, self.data)
        except:
            self.connection = None

    def load_previous_data(self):
        for position in POSITIONS:
            print(f"updating position {position}")
            if position in self.data.positions:
                self.graphs.update_notebook(position, self.data.positions[position])

    # def check_remote_data(self, device):
    #     print(f"checking remote data")
    #     self.data.get_missing_packets(device)

    def update_date(self):
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.data.update_date(self.today)
        print("send change date commands")
        for device in global_params.DEVICES:
            self.connection.send_command(device,
                                         {"command": "update date",
                                          "date": self.today})

    # def update_model(self, device):
    #     self.connection.update_model(device)

    def maintain_mqtt_connact(self):
        """ Loop to keep checking if mqtt is still contacted if computer
        went to sleep"""
        self.loop = self.after(10000, self.maintain_mqtt_connact)
        # TODO: fill in
        topic = "device_number/hub/status"
        msg = "check"
        print("MQTT check")
        self.mqtt_broker_checkin += 1
        if self.mqtt_broker_checkin >= 4:
            # the mqtt broker is not responding so try to restart
            print("Trying to reconnect mqtt")
            self.connect_mqtt()
        if self.connection:
            self.connection.publish(topic, msg)
        else:  # after coming out of sleep mode this will be called
            self.connect_mqtt()

    def save_data(self, data_type, device):
        print(f"saving data |{data_type}| for device_number: {device}")
        _file = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        if _file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        position = global_params.DEVICES[device]
        device_data = self.data.positions[position]
        if data_type == "Oryzanol":
            data_set = [device_data.oryzanol]
            _file.write(f"time, Oryzanol at {device}\n")
        elif data_type == "Temperature":
            print(f"saving temp data")
            data_set = [device_data.cpu_temp,
                        device_data.sensor_temp]
            _file.write(f"time, CPU Temp at {device}, Sensor Temp at {device}\n")
        times = device_data.time_series
        # times = [i.strftime('%H:%M:%S') for i in device_data.time_series]
        for i, time in enumerate(times):
            line_items = [time]
            for item in data_set:
                line_items.append(str(item[i]))
            line = ",".join(line_items)
            _file.write(line + '\n')

    def change_scan_params(self, device, packet):
        packet["command"] = "update scan params"
        self.connection.send_command(device, packet)

    # def check_sensor_settings(self, device):
    #     with open(os.path.join(__location__, "sensor_settings.json"), "r") as _file:
    #         data = json.load(_file)
    #     device_data = data[device]
    #     packet = {"command": "update signal chain"}
    #     packet["signal params"] = device_data
    #
    #     self.connection.send_command(device, packet)
    #     # update the graph so the reflectance data changes
    #     # the graph will get the data from sensor_settings.json
    #     self.graph.update_signal_processing(device)

    def get_remote_data(self):
        for device in global_params.DEVICES:
            self.connection.send_command(device,
                                         {"command": "send file list"})

    def restart_conn(self):
        self.connection.stop_conn()
        self.after(5000, self.connect_mqtt)

    def main_destroy(self):
        """
        Go through the connection and stop the mqtt loop and disconnect,
        then stop the thread in the graph to update the status labels,
        then quit, destory and exit, idk how many are actually
        needed but it works
        """
        if self.loop:
            self.after_cancel(self.loop)
        self.connection.destroy()
        #         self.graphs.destroy()
        self.quit()
        self.destroy()
        sys.exit()


if __name__ == '__main__':
    app = RBOGUI()
    app.title("Spectrograph")
    app.geometry("1250x650")
    app.protocol("WM_DELETE_WINDOW", app.main_destroy)
    app.mainloop()
