# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import tkinter as tk
import unittest

from GUI import info_frame


class TestSensorInfoFrame(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor_info_frame = info_frame.SensorInfoFrame(tk.Frame(),
                                                            tk.Tk(),
                                                            "device_1")

    def test_check_device(self):
        print(self.sensor_info_frame)
        print(self.sensor_info_frame.conn)
        self.sensor_info_frame.check_device()
