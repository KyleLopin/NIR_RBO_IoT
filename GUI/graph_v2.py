# Copyright (c) 2021-2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Version 2 of the graph programs to display
IoT sensor data
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
from datetime import datetime, timedelta
import json
import os
import tkinter as tk

# installed libraries
import matplotlib as mp
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle
from matplotlib import pyplot as plt
import numpy as np

# local files
import global_params
plt.style.use("seaborn")

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

DEVICES = global_params.DEVICES

COLORS = {"position 1": "orangered",
          "position 2": "mediumseagreen",
          "position 3": "darkblue",
          "CPU position 1": "darkred",
          "CPU position 2": "seagreen",
          "CPU position 3": "darkblue",
          "Sensor position 1": "coral",
          "Sensor position 2": "springgreen",
          "Sensor position 3": "dodgerblue",
          "AV": "slategray"}

with open(os.path.join(__location__, "master_settings.json")) as _file:
    json_data2 = _file.read()
# json_data2 = open(os.path.join(__location__, "master_settings.json")).read()
SETTINGS = json.loads(json_data2)
ORY_GRAPH_SIZE = (7, 3)
SPECTRUM_FRAME = (2.5, 2)
LABEL_SIZE = 14
SPECTRUM_LABEL_SIZE = 10
TICK_SIZE = 10
SPECTRUM_TICK_SIZE = 8
ROLL_ALPHA = 1.0
LINE_ALPHA = 0.2


class PyPlotFrame(tk.Frame):
    def __init__(self, parent, root_app: tk.Tk,
                 fig_size=(3, 3), xlabel=None,
                 ylabel=None, xlim=None,
                 ylim=None):
        tk.Frame.__init__(self, master=parent)
        self.root_app = root_app
        self.config(bg='white')

        # routine to make and embed the matplotlib graph
        self.figure = mp.figure.Figure(figsize=fig_size)
        self.figure.subplots_adjust(bottom=0.2)
        self.axis = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        if ylabel:
            self.axis.set_ylabel(ylabel, size=LABEL_SIZE)
        if xlabel:
            self.axis.set_xlabel(xlabel, size=LABEL_SIZE)
            if "Time" in xlabel:
                self.axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        if ylim:
            self.axis.set_ylim(ylim)
        if xlim:
            self.axis.set_xlim(xlim)
        else:  # can cause error if not set on raspberry pi python 3.7
            now = datetime.now()
            self.axis.set_xlim([now-timedelta(minutes=5), now+timedelta(minutes=5)])

        self.axis.tick_params(axis='both', labelsize=TICK_SIZE)

        plt.tight_layout()
        self.canvas.draw()
        self.lines = {}
        self.rolling_samples = SETTINGS["Rolling samples"]
        self.mean_lines = {}

        self.motion_connect = None
        self.rect = None
        self.zoom_coords = []
        self.zoomed = False
        self.canvas.mpl_connect("button_press_event", self._button_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)

    def update(self, x, y, label=None,
               show_mean=True):
        # print(f"update: {label}, {len(y)}, {len(x)}")
        # print(f"update lines: {self.lines}")
        # print(f"updatex: {x}")
        if len(y) != len(x):
            print(f"error in {label} data, len s: {len(x)}, {len(y)}")
            print(x)
            print(y)
            return
        if len(x) == 0:  # sometimes the sensor data will just be
            # invalid measurements so this will get called with no data
            return

        if show_mean:
            rolling_data = self.rolling_avg(y)
        _color = "blue"  # reflectance data

        if label:
            _color = COLORS[label]
        else:
            label = "blank"

        if label not in self.lines:
            marker = "-o"
            if label == "blank":
                marker = "-"
            self.lines[label], = self.axis.plot(x, y, marker,
                                                alpha=LINE_ALPHA,
                                                label=label,
                                                color=_color)
            if label != "blank":
                self.axis.legend(prop={'size': LABEL_SIZE})
            if show_mean:
                self.mean_lines[label], = self.axis.plot(x, rolling_data, '--',
                                                         color=_color,
                                                         alpha=ROLL_ALPHA)
        else:
            self.lines[label].set_xdata(x)
            self.lines[label].set_ydata(y)

            if show_mean:
                self.mean_lines[label].set_xdata(x)
                self.mean_lines[label].set_ydata(rolling_data)

        if not self.zoomed and label != "blank":
            # print("relim axis")
            self.axis.relim()
            self.axis.autoscale()
            # tick_skips = len(x) // 6
            # print(f"tick skips: {tick_skips}")
            # self.axis.set_xticks(self.axis.get_xticks()[::tick_skips])
        # print("Updata in graph_v2; drawing")
        self.canvas.draw()

    def rolling_avg(self, _list):
        _rolling_avg = []
        for i in range(1, len(_list) + 1):
            if (i - self.rolling_samples) > 0:
                avg = sum(_list[i - self.rolling_samples:i]) / self.rolling_samples
            else:
                # print(_list)
                avg = sum(_list[:i]) / i
            _rolling_avg.append(avg)
        return _rolling_avg

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
