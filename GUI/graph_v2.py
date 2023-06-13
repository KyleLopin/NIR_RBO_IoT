# Copyright (c) 2021-2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Version 2 of the graph programs to display
IoT sensor data.  Will embed a pyplot in a tkinter Frame,
will return a tk.Frame
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from datetime import datetime, timedelta
import json
import logging
import os
from random import randint
import statistics
import tkinter as tk
from typing import List, Tuple
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

# installed libraries
import matplotlib as mp
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# local files
import global_params
from displays.collapsible_frame import CollapsibleFrame
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
    """
    A custom Tkinter frame that embeds a pyplot graph.

    Attributes:
        root_app (tk.Tk): The root application.
        ylim (List[float]): The limits for the y-axis.
        figure (mp.figure.Figure): The pyplot figure.
        left_axis (mp.axes.Axes): The axes of the figure.
        canvas (FigureCanvasTkAgg): The canvas to display the figure.
        lines (dict): A dictionary of lines in the graph.
    """
    def __init__(self, parent, root_app: tk.Tk,
                 fig_size: Tuple[int, int] = (3, 3),
                 xlabel: str = None,
                 ylabel: str = None,
                 xlim: List[float] = None,
                 ylim: List[float] = None,
                 ylim_buttons: List[Tuple[str, int, int]] = None,
                 rhs_buttons: Tuple[str, str, str] = None,
                 hlines: List[float] = None,
                 use_log: bool =False):
        """
        Initialize the PyPlotFrame.

        Args:
            parent: The parent widget.
            root_app (tk.Tk): The root application.
            fig_size (Tuple[int, int], optional): The size of the figure. Defaults to (3, 3).
            xlabel (str, optional): The label for the x-axis. Defaults to None.
            ylabel (str, optional): The label for the y-axis. Defaults to None.
            xlim (List[float], optional): The limits for the x-axis. Defaults to None.
            ylim (List[float], optional): The limits for the y-axis. Defaults to None.
            ylim_buttons (List[Tuple[str, int, int]], optional): To make buttons to
            a collapsible frame that will let the user change the y-axis limits.  Pass in
            a list of tuples with the format (string to put on first line of the description, int
            of the bottom y lim, int of top of y lim).
            rhs_buttons (Tuple[str, str, str], optional): Right-hand side buttons to
            add the option of displaying the data using the right hand side of the graph. Leave
            blank if you do not want to use the rhs.
            hlines (List[float], optional): Horizontal lines to be displayed on the graph. Defaults to None.
            use_log (bool, optional): Whether to use a logarithmic scale on the y-axis. Defaults to False.
        """
        tk.Frame.__init__(self, master=parent)
        self.root_app = root_app
        self.ylim = ylim
        self.config(bg='white')

        # make buttons to change y-axis limits if used
        if ylim_buttons:
            # button_frame = tk.Frame(self)
            button_frame = CollapsibleFrame(self,
                                            closed_button_text="Show y axis options",
                                            open_button_text="Collapse options",
                                            collapsed=False, side="left", bg="white")
            for button_opt in ylim_buttons:
                button_text = f"{button_opt[0]}\n({button_opt[1]:,}-{button_opt[2]:,})"
                tk.Button(button_frame.collapsible_frame, text=button_text, width=15,
                          command=lambda a=button_opt[1], b=button_opt[2]: self.update_ylim(a, b)
                          ).pack(side=tk.TOP, pady=10)
            button_frame.pack(side="left", fill="y")

        # routine to make and embed the matplotlib graph
        self.figure = mp.figure.Figure(figsize=fig_size)
        self.figure.subplots_adjust(bottom=0.2)
        self.left_axis = self.figure.add_subplot(111)

        self.right_axis = None
        if rhs_buttons:
            _collapsed = True  # flag to set if frame should start being shown with the rhs axis labels
            self.right_axis = self.left_axis.twinx()
            self.rhs_collapse_frame = CollapsibleFrame(self,
                                                       closed_button_text="Show right y axis options",
                                                       open_button_text="Collapse options",
                                                       collapsed=_collapsed,
                                                       extra_command=self.add_right_axis,
                                                       side="right", bg="white")
            if _collapsed:
                self.remove_right_axis()

            for button_opt in ylim_buttons:
                button_text = f"{button_opt[0]}\n({button_opt[1]:,}-{button_opt[2]:,})"
                tk.Button(self.rhs_collapse_frame.collapsible_frame, text=button_text,
                          width=15,
                          command=lambda a=button_opt[1], b=button_opt[2]: self.update_ylim(a, b, "right")
                          ).pack(side=tk.TOP, pady=10)
            self.rhs_collapse_frame.pack(side="right", fill="y")

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if ylabel:
            self.left_axis.set_ylabel(ylabel, size=LABEL_SIZE)
        if xlabel:
            self.left_axis.set_xlabel(xlabel, size=LABEL_SIZE)
            if "Time" in xlabel:
                self.left_axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        if ylim:
            self.left_axis.set_ylim(ylim)
        if xlim:
            self.left_axis.set_xlim(xlim)

        if use_log:
            self.left_axis.set_yscale('log')

        else:  # can cause error if not set on raspberry pi python 3.7
            now = datetime.now()
            self.left_axis.set_xlim([now - timedelta(minutes=5), now + timedelta(minutes=5)])

        self.left_axis.tick_params(axis='both', labelsize=TICK_SIZE)

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
                self.left_axis.axhline(y=hline, color=HLINE_COLORS[i],
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
            self.lines[label], = self.left_axis.plot(x, y, marker,
                                                     alpha=LINE_ALPHA,
                                                     label=label,
                                                     color=_color)
            if label != "blank":
                self.left_axis.legend(prop={'size': LABEL_SIZE})
            if show_mean:
                self.mean_lines[label], = self.left_axis.plot(x, rolling_data, '--',
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
            # print("re-limit axis", self.ylim)
            self.left_axis.relim()
            self.left_axis.autoscale()
            # if self.ylim:  # TODO: test if this is needed
            #     # print("setting ylim")
            #     self.left_axis.set_ylim(self.ylim)
            # tick_skips = len(x) // 6
            # print(f"tick skips: {tick_skips}")
            # self.axis.set_xticks(self.axis.get_xticks()[::tick_skips])
        # print("Update in graph_v2; drawing")
        self.canvas.draw()

    def toggle_right_axis(self):
        print(f"Toggling the right hand size axis")
        print(f"visible: {self.rhs_collapse_frame.collapsible_frame.winfo_ismapped()}")

    def remove_right_axis(self):
        """
        Remove the right-hand side axis labels and tick marks.
        """
        # self.right_axis.set_yticks([])  # Remove the tick marks
        # self.right_axis.set_yticklabels([])  # Remove the tick labels
        self.right_axis.tick_params(axis='y', left=False,
                                    right=False, labelleft=False, labelright=False)

    def add_right_axis(self):
        """
        Add back the right-hand side axis labels and tick marks.
        """
        print("adding right axis")
        # self.right_axis.set_yticks([])  # Clear any existing tick marks
        # self.right_axis.set_yticklabels([])  # Clear any existing tick labels
        self.right_axis.tick_params(axis='y', left=False,
                                    right=True, labelleft=False, labelright=True)
        self.right_axis.spines['right'].set_visible(True)  # Show the right spine
        self._set_ylim(self.ylim[0], self.ylim[1], use_axis="right")

    def update_ylim(self, y_low, y_high, use_axis="left"):
        # print(f"Updating the ylim: {y_low}, {y_high}")
        self.ylim = [y_low, y_high]
        self._set_ylim(y_low, y_high, use_axis=use_axis)

    def rolling_avg(self, _list):
        """
        Calculate the rolling average of a list.  From ChatGPT

        Args:
            _list (list): The input list of values.

        Returns:
            list: The list of rolling averages.

        """
        _rolling_avg = [
            statistics.mean(_list[max(0, i - self.rolling_samples):i])
            for i in range(1, len(_list) + 1)
        ]
        return _rolling_avg

    def rolling_avg_depr(self, _list):
        _rolling_avg = []
        for i in range(1, len(_list) + 1):
            if (i - self.rolling_samples) > 0:
                avg = sum(_list[i - self.rolling_samples:i]) / self.rolling_samples
            else:
                # print(_list)
                avg = sum(_list[:i]) / i
            _rolling_avg.append(avg)
        return _rolling_avg

    def _set_ylim(self, y1, y2, use_axis="left"):
        """
        Set the y-axis limits for the specified axis.

        Args:
            y1 (float): The lower limit of the y-axis.
            y2 (float): The upper limit of the y-axis.
            use_axis (str, optional): The axis to set the y-axis limits for.
                Valid values are 'left' and 'right'. Defaults to 'left'.

        Raises:
            ValueError: If the value for 'use_axis' is invalid.

        """
        # Determine the axis to use based on the 'use_axis' parameter
        if use_axis == "left":
            axis = self.left_axis
        elif use_axis == "right":
            axis = self.right_axis
        else:
            # Raise an exception if 'use_axis' has an invalid value
            raise ValueError("Invalid value for 'use_axis'. Expected 'left' or 'right'.")

        # Set the y-axis limits based on the given values
        if y1 > y2:
            axis.set_ylim([y2, y1])  # Reverse the order if y1 is greater than y2
        else:
            axis.set_ylim([y1, y2])

        # Redraw the canvas to reflect the changes
        self.canvas.draw()

    def _set_xlim(self, x1, x2):
        """
        Set the x-axis limits.

        Args:
            x1 (float): The lower limit of the x-axis.
            x2 (float): The upper limit of the x-axis.

        """
        # Determine the correct order of the limits
        if x1 > x2:
            # If x1 is greater than x2, reverse the order
            self.left_axis.set_xlim([x2, x1])
        else:
            # Otherwise, use the limits as is
            self.left_axis.set_xlim([x1, x2])

        # Redraw the canvas to reflect the changes
        self.canvas.draw()


if __name__ == '__main__':
    MOCK_RANGE = [2000, 10000]
    time_data = []
    y_data = []


    def mock_data():
        y_data.append(randint(MOCK_RANGE[0], MOCK_RANGE[1]))
        time_data.append(datetime.now())
        plot.update_graph(time_data, y_data, show_mean=True)

    root = tk.Tk()
    # plot = PyPlotFrame(root, root,
    #                    fig_size=(9, 4),
    #                    ylim=[0, 16000],
    #                    hlines=[3500, 5000, 8000, 10000])
    plot = PyPlotFrame(root, root,
                       fig_size=(9, 4),
                       ylabel="Oryzanol Concentrations",
                       xlabel="Time",
                       ylim=[0, 16000],
                       hlines=[3500, 5000, 8000, 10000],
                       ylim_buttons=global_params.ORY_GRAPH_BUTTON_OPTS,
                       rhs_buttons=global_params.RHS_BUTTON_OPTS)

    tk.Button(root, text="mock data", command=mock_data).pack(side="bottom")
    # plot.update_graph([datetime(2023, 2, 24, 0, 1, 51),
    #                    datetime(2023, 2, 24, 0, 4, 51)], [1, -5])
    plot.pack()
    root.mainloop()
