# Copyright (c) 2021-2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Version 2 of the graph programs to display
IoT sensor data
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from datetime import datetime, timedelta
import json
import os
import tkinter as tk

# installed libraries
import matplotlib as mp
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# local files
import global_params
# plt.style.use("seaborn")
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
HLINE_COLORS = ['goldenrod', 'goldenrod',
                'darkgoldenrod', 'darkgoldenrod']

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
                 ylim=None, allow_zoom=False,
                 hlines: list = None,
                 use_log=False):
        tk.Frame.__init__(self, master=parent)
        self.root_app = root_app
        self.allow_zoom = allow_zoom
        self.ylim = ylim
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

        if use_log:
            self.axis.set_yscale('log')

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

        if hlines:
            for i, hline in enumerate(hlines):
                self.axis.axhline(y=hline, color=HLINE_COLORS[i],
                                  ls='--')

    def update_graph(self, x, y, label=None,
                     show_mean=True):
        """

        Args:
            x: list[datetime.datetime]
            y:
            label:
            show_mean:

        Returns:

        """
        # print(f"update: {label}, {len(y)}, {len(x)}")
        # print(f"update lines: {self.lines}")
        # print(f"update x: {x}")
        if len(y) != len(x):
            print(f"error in {label} data, len s: {len(x)}, {len(y)}")
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
            self.lines[label].set_xdata(mdates.date2num(x))
            self.lines[label].set_ydata(y)

            if show_mean:
                self.mean_lines[label].set_xdata(mdates.date2num(x))
                self.mean_lines[label].set_ydata(rolling_data)

        # print(f"check1 {self.zoomed}, {label}")
        if not self.zoomed and label != "blank":
            print("re-limit axis", self.ylim)
            self.axis.relim()
            self.axis.autoscale()
            if self.ylim:
                # print("setting ylim")
                self.axis.set_ylim(self.ylim)
            # tick_skips = len(x) // 6
            # print(f"tick skips: {tick_skips}")
            # self.axis.set_xticks(self.axis.get_xticks()[::tick_skips])
        print("Update in graph_v2; drawing")
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


if __name__ == '__main__':
    root = tk.Tk()
    # plot = PyPlotFrame(root, root,
    #                    fig_size=(9, 4),
    #                    ylim=[0, 16000],
    #                    hlines=[3500, 5000, 8000, 10000])
    plot = PyPlotFrame(root, root,
                       fig_size=(9, 4),
                       ylim=[0.1, 100],
                       use_log=True)
    plot.update_graph([datetime(2023, 2, 24, 0, 1, 51),
                       datetime(2023, 2, 24, 0, 4, 51)], [1, -5])
    plot.pack()
    root.mainloop()
