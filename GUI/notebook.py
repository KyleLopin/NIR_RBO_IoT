# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import json
import os
import tkinter as tk
from tkinter import ttk

# installed libraries
import numpy as np

# local file
import global_params
import graph_v2 as graph

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, "new_models.json")) as _file:
    json_data = _file.read()
MODEL_INFO = json.loads(json_data)
DEVICES = global_params.DEVICES
POSITIONS = global_params.POSITIONS
WAVELENGTHS = [i for i in range(1350, 1651)]


def divide(list1: list, list2: list):
    result = []
    for num1, num2 in zip(list1, list2):
        result.append(float(num1)/float(num2))
    return result


class Notebook(tk.Frame):
    def __init__(self, root_app: tk.Tk):
        self.root_app = root_app
        tk.Frame.__init__(self, master=root_app)
        notebook = ttk.Notebook(root_app)
        notebook.pack(expand=True, fill=tk.BOTH)

        self.ory_plot = graph.PyPlotFrame(notebook, root_app,
                                          fig_size=(9, 4),
                                          ylabel="Oryzanol Concentrations",
                                          xlabel="Time",
                                          xlim=[0, 16000],
                                          hlines=[3500, 5000, 8000, 10000])
        self.ory_plot.pack()
        self.av_plot = graph.PyPlotFrame(notebook, root_app,
                                         fig_size=(9, 4),
                                         ylabel="Acid Value",
                                         xlabel="Time",
                                         ylim=[0.1, 100],
                                         use_log=True)
        self.av_plot.pack()
        self.temp_plot = graph.PyPlotFrame(notebook, root_app,
                                           fig_size=(9, 4),
                                           ylabel="Temperature",
                                           xlabel="Time",
                                           allow_zoom=True)
        self.temp_plot.pack()

        _refl_frame = tk.Frame(notebook)
        self.refl_plots = dict()
        for position in global_params.POSITIONS:
            # print(position)
            _plt = graph.PyPlotFrame(_refl_frame, root_app,
                                     fig_size=(3, 4),
                                     ylabel="Reflectane",
                                     xlabel="Wavelengths (nm)",
                                     ylim=[0, 1.5], xlim=[1350, 1650])
            _plt.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.refl_plots[position] = _plt
        _refl_frame.pack()

        notebook.add(self.ory_plot, text="Oryzanol")
        notebook.add(self.av_plot, text="AV")
        notebook.add(self.temp_plot, text="Temperature")
        notebook.add(_refl_frame, text="Reflectance")

    def update(self, position, data):
        # print("pp", data.time_series)
        # print(type(data))
        self.update_temp(data.time_series,
                         data.cpu_temp,
                         data.sensor_temp,
                         position)
        self.update_ory(data.time_series,
                        data.oryzanol, position)
        if position == "position 1" or position == "position 2":
            print(f"updating AV")
            print(data.av)
            self.update_av(data.time_series,
                           data.av, position)

    def update_spectrum(self, raw_data, position):
        # TODO: convert the models from device_number to positions
        device = POSITIONS[position]
        print("ff", self.refl_plots.keys(), device)
        reference_data = MODEL_INFO[device]["Ref Intensities"]
        reflectance_data = divide(raw_data, reference_data)
        self.refl_plots[position].update(WAVELENGTHS,
                                         reflectance_data,
                                         show_mean=False)

    def update_ory(self, time, ory_conc, _position):
        self.ory_plot.update(time, ory_conc,
                             label=_position)

    def update_av(self, time, av, device):
        # print("update av")
        self.av_plot.update(time, av,
                            label=device)

    def update_temp(self, time, cpu_temp,
                    sensor_temp, _position):
        sensor_mask = np.ma.masked_not_equal(np.array(sensor_temp), 0.0)

        self.temp_plot.update(time, cpu_temp,
                              label=f"CPU {_position}",
                              show_mean=False)
        # print(sensor_mask)
        # print(np.array(time)[sensor_mask.mask])
        if len(time) != len(sensor_mask.mask) or \
                len(sensor_temp) != len(sensor_mask.mask):
            print("Error in lent of sensor temp mask")
            print(f"len time {len(np.array(time)[sensor_mask.mask])}"
                  f" len temp {len(np.array(sensor_temp)[sensor_mask.mask])}")
            print(np.array(time)[sensor_mask.mask])
            print(np.array(sensor_temp)[sensor_mask.mask])
        self.temp_plot.update(np.array(time)[sensor_mask.mask],
                              np.array(sensor_temp)[sensor_mask.mask],
                              label=f"Sensor {_position}",
                              show_mean=False)
