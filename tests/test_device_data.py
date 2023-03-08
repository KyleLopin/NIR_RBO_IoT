# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import os
import shutil
import sys
import unittest
from unittest import mock

sys.path.append(os.path.join('..', 'GUI'))
# local files
from GUI import data_class

DATA_POS2_1 = {'time': '09:55:22', 'date': '2022-11-18', 'packet_id': 1, 'device': 'position 2',
               'mode': 'live', 'OryConc': -20139, 'CPUTemp': '48.31', 'SensorTemp': 0, 'AV': -1}


class TestAddDataPkt(unittest.TestCase):
    """ Test that the DeviceData class in data_class
    add_data_pkt method works properly """
    def setUp(self) -> None:
        self.device_data = data_class.DeviceData(use_av=True)

    def test_add_pos_2(self):
        print(f"av1: {self.device_data.av}")
        self.assertListEqual(self.device_data.av, [])
        self.device_data.add_data_pkt(DATA_POS2_1, None)
        print(f"av2: {self.device_data.av}")
        self.assertListEqual(self.device_data.av, [-1.0])


