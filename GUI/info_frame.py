# Copyright (c) 2020-2021 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Make the frame to display the status of the sensors, a stop and start
button for the sensor and the temperature of the devices
"""

__author__ = "Kyle Vitatus Lopin"


# standard libraries
import tkinter as tk
# local files
import global_params

POSITIONS = global_params.POSITIONS
SENSOR_OFFLINE = 0
SENSOR_NOT_READING = 1
SENSOR_READING = 2

CHECK_IN_FAILS_TO_OFF = 5


class InfoFrame(tk.Frame):
    """ A tkinter frame to hold information on the 3 sensors """
    def __init__(self, root: tk.Tk, positions: list):
        tk.Frame.__init__(self, master=root)
        self.root_app = root
        self.sensor_frames = dict()
        self.temp_frames = dict()
        for position in positions:
            _frame = tk.Frame(self, relief=tk.GROOVE, bd=3)

            sensor_frame = SensorInfoFrame(_frame, root, position)
            sensor_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.sensor_frames[position] = sensor_frame

            temp_frame = TempFrame(_frame, position)
            temp_frame.pack(side=tk.LEFT)
            self.temp_frames[position] = temp_frame

            _frame.pack(side=tk.LEFT)

    def add_connection(self, _conn):
        for position in POSITIONS:
            self.sensor_frames[position].add_connection(_conn)

    def check_in(self, position):
        self.sensor_frames[position].checking_in()

    def position_online(self, device, is_running):
        self.sensor_frames[device].position_online(is_running)

    def update_temp(self, data_pkt, position):
        sensor_temp = "missing"
        cpu_temp = "missing"
        if "SensorTemp" in data_pkt:
            sensor_temp = data_pkt["SensorTemp"]
        if "CPUTemp" in data_pkt:
            cpu_temp = data_pkt["CPUTemp"]
        self.temp_frames[position].update_temp(cpu_temp,
                                             sensor_temp)


class SensorInfoFrame(tk.Frame):
    def __init__(self, parent_frame: tk.Frame,
                 master: tk.Tk, _position: str):
        tk.Frame.__init__(self, master=parent_frame)
#         print("Making info frame")
        self.config(bg='white')
        self.master = master
#         print(f"position: {_position}")
        self.conn = None
        self.check_in = CHECK_IN_FAILS_TO_OFF + 1
        self.position = _position
        self.status_label = tk.Label(self, text=f"{_position} offline",
                                     bg='red')
        self.status_label.pack(side=tk.BOTTOM)
        self.status_button = tk.Button(self, text="Check Status",
                                       command=self.check_device)
        self.status_button.pack(side=tk.BOTTOM)
        self.sensor_state = SENSOR_OFFLINE  # just assume and check later
        self.update_online_status_labels()
        self.loop = None

    def check_device(self):
        print(f"checking device at {self.position}")
        device = self.position
        if self.sensor_state == SENSOR_OFFLINE:
            # check if the device is connected yet
            self.conn.check_connection(device)
        elif self.sensor_state == SENSOR_NOT_READING:
            # start the device reading
            self.conn.start_device(device)

        elif self.sensor_state == SENSOR_READING:
            # start the device reading
            self.conn.stop_device(device)

    def update_online_status_labels(self):
        """ Thread that will restart itself every 65 seconds
         to go through all the positions and check if they have sent data
         since the last check-in.
         Check in interval should be longer than reading interval."""
        # print(f"Updating device status| check in: {self.check_in}")
        # self.thread = threading.Timer(65, self.update_online_status_labels)
        # self.thread.start()
        self.loop = self.master.after(10000, self.update_online_status_labels)
        self.check_in += 1
        print(f"loop checkin for position: {self.position}, checkin: {self.check_in} ")
        if self.check_in > CHECK_IN_FAILS_TO_OFF:
            self.position_offline()
        else:  # check in is set True if it recieves data
            self.position_online(True)

    def checking_in(self):
        print(f"checkin position: {self.position}")
        self.check_in = 0

    def position_online(self, running: bool):
        # print(f"postion online status for {self.position}, running: {running}")
        if running:
            self.status_label.config(text=f"{self.position} online\nsensor running",
                                     bg="green")
            self.status_button.config(text="Stop sensor")
            self.sensor_state = SENSOR_READING
        else:
            self.status_label.config(text=f"{self.position} online\nsensor not running",
                                     bg="yellow")
            self.status_button.config(text="Start sensor")
            self.sensor_state = SENSOR_NOT_READING

        self.check_in = True

    def position_offline(self):
        # print(f"postion offline status, {self.position}")
        self.status_label.config(text=f"{self.position} offline\n ",
                                 bg="red")
        self.status_button.config(text="Check Status")
        self.sensor_state = SENSOR_OFFLINE

    def add_connection(self, device_connection):
        self.conn = device_connection

    def destroy(self):
        # print("destroying graph")
        if self.loop:
            self.master.after_cancel(self.loop)


class TempFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, _pos: str):
        tk.Frame.__init__(self, master=parent, bg="white")
        tk.Label(self, text=f"{_pos} temperature:",
                 bg="white").pack()
        self.cpu_temp_label = tk.Label(self, bg="white",
                                       text="No Temp read")
        self.cpu_temp_label.pack(side=tk.TOP)
        self.sensor_temp_label = tk.Label(self, bg="white",
                                          text="No Temp read")
        self.sensor_temp_label.pack(side=tk.TOP)

    def update_temp(self, cpu=None, sensor=None):
        self._update_temp(cpu, self.cpu_temp_label, "CPU")
        self._update_temp(sensor, self.sensor_temp_label, "Sensor")

    def _update_temp(self, _temp, _label: tk.Label, sensor: str):
        temp = float(_temp)  # incase its a string
        red_temp = 75
        yellow_temp = 65
        if _label == "Sensor":
            red_temp = 50
            yellow_temp = 40
        if temp > red_temp:
            color = 'red'
        elif temp > yellow_temp:
            color ='yellow'
        else:
            color = 'white'
        _label.config(text=f"{sensor} {temp:.1f}\u2103",
                      bg=color)
