# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
from datetime import datetime, timedelta
import json
import tkinter as tk
# installed libraries
import matplotlib as mp
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle
from matplotlib import pyplot as plt
import numpy as np
# local files
import data_class
import global_params
plt.style.use("seaborn")


SENSOR_OFFLINE = 0
SENSOR_NOT_READING = 1
SENSOR_READING = 2
DEBOUNCE_TIME = 300

TIME_OPTIONS = ["0:15", "0:30", "0:45",
                "1:00", "1:30", "2:00",
                "3:00", "4:00", "6:00"]
DEVICES = global_params.DEVICES
COLORS = {"device_1": "orangered",
          "device_2": "mediumseagreen",
          "device_3": "darkblue"}
json_data2 = open("master_settings.json").read()
SETTINGS = json.loads(json_data2)
DISPLAY_ROLLING_MEAN = SETTINGS["Rolling avg"]

# def get_settings(position, key):
#     json_data = open("sensor_settings.json").read()
#     json_settings = json.loads(json_data)
#     print(json_settings.keys())
#     print(json_settings["position 1"].keys())
#     return json_settings[position][key]
# print(get_settings("position 1", "Ref Intensities"))


class TimeSeriesPlotter(tk.Frame):
    def __init__(self, parent: tk.Tk, _size=(10, 4)):
        # self.data = None
        self.scale = None
        self.root_app = parent
        tk.Frame.__init__(self, master=parent)
        self.scale_index = 7

        # routine to make and embed the matplotlib graph
        self.figure = mp.figure.Figure(figsize=_size)
        self.figure.subplots_adjust(bottom=0.2)
        self.axis = self.figure.add_subplot(111)

        # self.figure.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # self.canvas.get_tk_widget().pack(side=tk.TOP)


        self.axis.set_ylabel("Oryzanol Concentrations", size=18)
        # self.axis.set_ylim([0, 50000)

        if self.scale:
            self.draw_xaxis()
        self.axis.set_xlabel(r'Time', size=18)
        self.axis.tick_params(axis='both', labelsize=14)
        # self.axis.set_xticklabels(self.axis.get_xticks(), rotation=45)
        self.axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.tight_layout()
        self.canvas.draw()
        self.lines = {}
        self.mean_lines = {}
        self.data = {}
        self.devices = {}

        sensor_frame = tk.Frame(self)
        temp_frame = tk.Frame(sensor_frame)
        # sides = [tk.LEFT, tk.LEFT, tk.RIGHT]
        self.temp_labels = {}
        for i, device in enumerate(DEVICES.keys()):
            self.data[device] = [[], [], []]
            self.devices[device] = SensorInfoFrame(sensor_frame,
                                                   parent, device)
            self.devices[device].pack(side=tk.LEFT, fill=tk.X)

            tk.Label(temp_frame, text=f"{DEVICES[device]} temperature:").pack()
            self.temp_labels[device] = []
            for i in range(2):
                # self.temp_labels[device][i].set("No Temp read")
                _l = tk.Label(temp_frame,
                              text="No Temp read")
                _l.pack(side=tk.TOP)
                self.temp_labels[device].append(_l)

            # self.devices[device].pack()
        # sensor_frame.pack(side=tk.BOTTOM, fill=tk.X)
        # makes temperature labels
        temp_frame.pack(side=tk.LEFT, fill=tk.Y)
        temp_frame.pack(side=tk.LEFT, fill=tk.Y)
        sensor_frame.pack(side=tk.BOTTOM)
        self.motion_connect = None
        self.rect = None
        self.zoom_coords = []
        self.zoomed = False
        self._click_thread = None
        self.canvas.mpl_connect("button_press_event", self._button_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)

    def add_data_class(self, _data):
        print("This doesnt work anymore")
        # self.data = _data

    def draw_xaxis22(self):
        if self.scale:
            now = datetime.now()
            start_time = now - self.scale
            end_time = now + timedelta(minutes=5)
            self.axis.set_xlim([start_time, end_time])
        else:
            self.axis.autoscale()

    def update(self, device, time, conc, rolling):
        if device not in self.lines:
            if DISPLAY_ROLLING_MEAN:
                self.mean_lines[device], = self.axis.plot(self.data[device][0],
                          self.data[device][2], "--",
                          color=COLORS[device])

            self.lines[device], = self.axis.plot(self.data[device][0],
                           self.data[device][1], "-o", alpha=0.7,
                           label=device, color=COLORS[device])

            self.axis.legend(prop={'size': 18})
        else:
            # print(self.lines[device])
            self.lines[device].set_ydata(conc)
            self.lines[device].set_xdata(time)
            self.mean_lines[device].set_ydata(rolling)
            self.mean_lines[device].set_xdata(time)

        # print("graph updating ", self.zoomed)
        if not self.zoomed:
            # print("axis relim")
            self.axis.relim()
            self.axis.autoscale()
        self.canvas.draw()

    def add_connection(self, _connection):
        for device in DEVICES.keys():
            self.devices[device].add_connection(_connection)

    def position_online(self, position,
                        running: bool):
        print(f"postion: {position} online status")
        device = global_params.POSITIONS[position]
        self.devices[device].position_online(running)

    def update_spectrum(self, reflectance, device):
        self.devices[device].spectrum_frame.update(reflectance)

    def update_temp(self, device, temp):
        self.temp_labels[device][0].config(text=f"CPU {temp}\u2103")
        temp = float(temp)  # incase its a string
        if temp > 75:
            self.temp_labels[device][0].config(bg='red')
        elif temp > 65:
            self.temp_labels[device][0].config(bg='yellow')
        else:
            self.temp_labels[device][0].config(bg='white')

    def check_in(self, device):
        self.devices[device].check_in = True

    def _on_release(self, event):
        print(f"release: {event}")
        if not self.zoom_coords:
            print("releasing double click or off graph first click")
            return  # this is the release from double button press

        if event.xdata: # on graph
            end_time = mdates.num2date(event.xdata)
        elif self.rect:
            # the release is off the graph
            if event.x < 250:  # released off left side of graph
                self.axis.set_xlim(right=self.zoom_coords[0])
            elif event.x > 750:  # released off right side of graph
                self.axis.set_xlim(left=self.zoom_coords[0])
            else: # middle of x axis
                # set the y lim only
                pass  # doesn't work
                # if self.zoom_coords[1] > event.ydata:
                #     self.axis.set_ylim([event.ydata, self.zoom_coords[1]])
                # else:
                #     self.axis.set_ylim([self.zoom_coords[1], event.ydata])
            if event.y < 150:  # released off bottom
                self.axis.set_ylim(top=self.zoom_coords[1])
            elif event.y > 250:
                self.axis.set_ylim(bottom=self.zoom_coords[1])
            self.rect.remove()
            self.rect = None
            self.zoomed = True

        if self.rect and event.xdata:
            self.rect.remove()
            self.rect = None
            # now zoom in
            # print("zooming in")
            start_time = self.zoom_coords[0]
            end_time = mdates.num2date(event.xdata)
            self._set_xlim(start_time, end_time)

            self._set_ylim(self.zoom_coords[1], event.ydata)
            # check if end_time is close enough to the end
            self.zoomed = True
        self.canvas.mpl_disconnect(self.motion_connect)
        self.canvas.draw()

    def _button_press(self, event):
        if event.dblclick:
            # print("Double clicked")
            self._double_click(event)
            return
        if not event.xdata:
            return
        # zoom in on the coords
        # print("button press")
        # print(event)
        t0 = mdates.num2date(event.xdata)
        y0 = event.ydata
        self.zoom_coords = [t0, event.ydata]
        self.rect = Rectangle((t0, y0), timedelta(seconds=1), 0,
                              facecolor='None', edgecolor='slategrey',
                              lw=2, ls='--')
        self.axis.add_patch(self.rect)
        # print("finish button press")
        self.motion_connect = self.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def _single_click_dep(self, event):
        if event.xdata:  # else pass, not on graph
            # zoom in on the coords
            # print("single click")
            self._click_thread = None
            # print(event)
            x0 = event.xdata
            y0 = event.ydata
            # self.zoom_coords = [event.xdata, event.ydata]
            time = mdates.num2date(event.xdata)
            # print(f"x: {x0}, y0: {y0}, time: {time.strftime('%H:%M:%S')}")

    def _on_motion(self, event):
        if event.xdata:
            x1 = mdates.num2date(event.xdata)
            y1 = event.ydata
            self.rect.set_width(x1 - self.zoom_coords[0])
            self.rect.set_height(y1 - self.zoom_coords[1])
            self.rect.set_xy(self.zoom_coords)
            self.canvas.draw()
        else:
            if event.x < 250:
                # is off the left side of the graph, snap to side
                pass

    def _double_click(self, event):
        self.zoom_coords = []
        self.zoomed = False
        self.axis.relim()
        self.axis.autoscale()
        self.canvas.draw()

    def _set_ylim(self, y1, y2):
        if y1 > y2:
            self.axis.set_ylim([y2, y1])
        else:
            self.axis.set_ylim([y1, y2])

    def _set_xlim(self, x1, x2):
        if x1 > x2:
            self.axis.set_xlim([x2, x1])
        else:
            self.axis.set_xlim([x1, x2])


class SpectrumFrame(tk.Frame):
    def __init__(self, master, _size=(3.5, 4)):
        tk.Frame.__init__(self, master=master)
        self.data = None
        # routine to make and embed the matplotlib graph
        self.figure = mp.figure.Figure(figsize=_size)
        self.axis = self.figure.add_subplot(111)
        # self.bar = self.figure.add_subplot(122)

        # self.figure.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure, master)
        # self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.axis.set_ylabel("Reflectance", size=18)
        self.axis.set_xlabel(r'Wavelenght (nm)', size=18)
        self.axis.set_xlim([1350, 1650])
        self.axis.set_ylim([0, 1.0])
        # plt.gcf().subplots_adjust(bottom=0.45)
        # plt.tight_layout(w_pad=1, h_pad=3)
        self.figure.subplots_adjust(bottom=0.21,
                                    left=0.17)
        wavelengths = [i for i in range(1350, 1651)]
        # print(wavelengths)
        self.line, = self.axis.plot(wavelengths, wavelengths)
        self.canvas.draw()

    def update(self, reflectance_data):
        # print("updating spectrum data")
        # print(reflectance_data)
        self.line.set_ydata(reflectance_data)
        # print(self.line.get_xydata())
        # wavelengths = [i for i in range(1350, 1651)]
        # self.axis.plot(wavelengths, reflectance_data)
        self.canvas.draw()


class SensorInfoFrame(tk.Frame):
    def __init__(self, parent_frame: tk.Frame, master: tk.Tk, _position):
        tk.Frame.__init__(self, master=parent_frame)
        self.master = master
        self.spectrum_frame = SpectrumFrame(self)
        # self.spectrum_frame.pack(side=tk.TOP)

        self.conn = None
        self.check_in = False
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
        print(f"Updating device status| check in: {self.check_in}")
        # self.thread = threading.Timer(65, self.update_online_status_labels)
        # self.thread.start()
        self.loop = self.master.after(65000, self.update_online_status_labels)
        if not self.check_in:
            self.position_offline()
        else:  # check in is set True if it recieves data
            self.position_online(True)
        self.check_in = False

    def checking_in(self):
        self.check_in = True

    def position_online(self, running: bool):
        print(f"postion online status for {self.position}")
        if running:
            self.status_label.config(text=f"{DEVICES[self.position]} online\nsensor running",
                                     bg="green")
            self.status_button.config(text="Stop sensor")
            self.sensor_state = SENSOR_READING
        else:
            self.status_label.config(text=f"{DEVICES[self.position]} online\nsensor not running",
                                     bg="yellow")
            self.status_button.config(text="Start sensor")
            self.sensor_state = SENSOR_NOT_READING

        self.check_in = True

    def position_offline(self):
        # print("postion offline status")
        self.status_label.config(text=f"{DEVICES[self.position]} offline\n ",
                                 bg="red")
        self.sensor_state = SENSOR_OFFLINE

    def add_connection(self, device_connection):
        self.conn = device_connection
        # send message to the device
        # to see who is online when the gui starts
        self.conn.check_connection(self.position)

    def destory(self):
        print("destroying graph")
        self.master.after_cancel(self.loop)
        tk.after_cancel(self.loop)

# class StatusFrame(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master=master)
#         self.config(bg='green')
#         self.conn = None
#         self.status_labels = dict()
#         self.buttons = dict()
#         self.check_in = dict()
#         self.sensor_states = dict()
#         self.make_device_frames()
#         self.thread = None
#         self.update_online_status_labels()
#
#     def add_connection(self, device_connection):
#         self.conn = device_connection
#         # send messages to all the devices
#         # to see who is online when the gui starts
#         self.conn.check_connections()
#
#     def make_device_frames(self):
#         for position in global_params.POSITIONS.keys():
#             _frame = tk.Frame(self)
#             print(position)
#             self.check_in[position] = False
#             status_label = tk.Label(_frame, text=f"{position} offline",
#                                     bg='red')
#             status_label.pack(side=tk.BOTTOM, pady=4)
#             self.status_labels[position] = status_label
#
#             self.buttons[position] = tk.Button(_frame, text="Check Status",
#                                                command=lambda pos=position: self.check_device(pos))
#             self.buttons[position].pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
#             _frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#             self.sensor_states[position] = SENSOR_OFFLINE  # just assume and check later
#
#     def check_device(self, position):
#         print(f"checking device at {position}")
#         device = DEVICES[position]
#         if self.sensor_states[position] == SENSOR_OFFLINE:
#             # check if the device is connected yet
#             self.conn.check_connection(device)
#         elif self.sensor_states[position] == SENSOR_NOT_READING:
#             # start the device reading
#             self.conn.start_device(device)
#
#         elif self.sensor_states[position] == SENSOR_READING:
#             # start the device reading
#             self.conn.stop_device(device)
#
#     def update_online_status_labels(self):
#         """ Thread that will restart itself every 65 seconds
#          to go through all the positions and check if they have sent data
#          since the last check-in.
#          Check in interval should be longer than reading interval."""
#         print("Updating device status")
#         # self.thread = threading.Timer(65, self.update_online_status_labels)
#         # self.thread.start()
#         self.master.after(65000, self.update_online_status_labels)
#         for position in global_params.POSITIONS:
#             if not self.check_in[position]:
#                 self.position_offline(position)
#
#     def checking_in(self, position):
#         self.check_in[position] = True
#
#     def position_online(self, position, running: bool):
#         print("postion online status")
#         if running:
#             self.status_labels[position].config(text=f"{position} online\nsensor running",
#                                                 bg="green")
#             self.buttons[position].config(text="Stop sensor")
#             self.sensor_states[position] = SENSOR_READING
#         else:
#             self.status_labels[position].config(text=f"{position} online\nsensor not running",
#                                                 bg="yellow")
#             self.buttons[position].config(text="Start sensor")
#             self.sensor_states[position] = SENSOR_NOT_READING
#
#         self.check_in[position] = True
#
#     def position_offline(self, position):
#         # print("postion offline status")
#         self.status_labels[position].config(text=f"{position} offline\n ", bg="red")
#         self.sensor_states[position] = SENSOR_OFFLINE


class TimeScale(tk.Frame):
    def __init__(self, master, graph):
        tk.Frame.__init__(self, master=master)
        self.current_state = "Full"
        self.graph = graph
        radio_frame = tk.Frame(self)
        tk.Label(radio_frame, text="Display Time options:").pack(side=tk.TOP)
        self.time_option = tk.StringVar(value=self.current_state)
        r1 = tk.Radiobutton(radio_frame, text="Full day of data",
                            value="Full", variable=self.time_option,
                            command=self.resize_to_scale)
        r2 = tk.Radiobutton(radio_frame, text="Enter time range",
                            value="Range", variable=self.time_option,
                            command=self.resize_to_scale)
        r1.pack(side=tk.LEFT)
        r2.pack(side=tk.LEFT)
        radio_frame.pack(side=tk.TOP)

        self.time_var = tk.StringVar(value="0:30")
        spinbox = tk.Spinbox(self, values=TIME_OPTIONS,
                             textvariable=self.time_var,
                             wrap=True, width=10,
                             command=self.resize_to_scale)
        spinbox.pack(side=tk.RIGHT)

    def resize_to_scale(self):
        print("resizing", self.current_state, self.time_option.get())
        print(self.current_state != self.time_option)
        # change the time scale
        if self.time_option.get() == "Full":
            print("Set full day scale")
            self.graph.scale = None
        elif self.time_option.get() == "Range":
            print("Set scale of", self.time_var.get())
            # self.graph.scale = self.time_var.get()
            t = datetime.strptime(self.time_var.get(),
                                  "%H:%M")
            self.graph.scale = timedelta(hours=t.hour,
                                         minutes=t.minute)
        self.graph.update()

