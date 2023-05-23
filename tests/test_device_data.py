# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Unit tests for the DeviceData class in the data_class.py file
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import os
import sys
import unittest
from unittest import mock

sys.path.append(os.path.join('..', 'GUI'))
# local files
from GUI import data_class

DATA_POS2_1 = {'time': '09:55:22', 'date': '2022-11-18', 'packet_id': 1, 'device': 'position 2',
               'mode': 'live', 'OryConc': -20139, 'CPUTemp': '48.31', 'SensorTemp': 0, 'AV': -1}
DATA_PKT1 = {'time': '09:55:22', 'date': '2022-11-18', 'packet_id': 1, 'device': 'position 2',
             'mode': 'live', 'OryConc': -10000, 'CPUTemp': '48.31', 'SensorTemp': 0, 'AV': 10}


class TestAddDataPkt(unittest.TestCase):
    """ Test that the DeviceData class in data_class
    add_data_pkt method works properly """
    def setUp(self) -> None:
        self.device_data = data_class.DeviceData(use_av=True)

    def test_add_pos_2(self):
        # print(f"av1: {self.device_data.av}")
        self.assertListEqual(self.device_data.av, [])
        self.device_data.add_data_pkt(DATA_POS2_1, None)
        # print(f"av2: {self.device_data.av}")
        self.assertListEqual(self.device_data.av, [-1.0])


class TestRollingAverage(unittest.TestCase):
    """ Test that the rolling average method works correctly """
    def setUp(self) -> None:
        self.device_data = data_class.DeviceData(use_av=True)
        self.device_data.rolling_samples = 5

    def test_rolling_avg(self):
        # self.device_data.add_data_pkt(DATA_PKT1, None)
        # print(self.device_data.av)
        # print(self.device_data.av_rolling)
        # print("=======")

        _list1 = [10, 11, 12]
        rolling_list = self.device_data.rolling_avg(_list1)
        print(rolling_list)
        ans1 = [10.0, 10.5, 11.0]
        self.device_data.av = [10.0]
        # self.device_data.rolling_avg()

        self.assertListEqual(rolling_list, ans1)
        _list2 = [10, 11, 12, 13, 14, 15, 14, 13]
        rolling_list = self.device_data.rolling_avg(_list2)
        print(rolling_list)
        ans2 = [10.0, 10.5, 11.0, 11.5, 12.0, 13.0, 13.6, 13.8]
        self.assertListEqual(rolling_list, ans2)
