# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Test
"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import datetime as dt
import json
import os
import sys
import unittest
from unittest import mock

# installed libraries
import freezegun

sys.path.append(os.path.join('..', 'GUI'))
# local files
import data_class
date_str = dt.datetime.today().strftime('%Y-%m-%d').encode('utf-8')
print(f"data string: {date_str}")


DATA_PKT1 = b'{"time": "09:55:22", "date": "2022-11-18", "packet_id": 1, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20139, ' \
            b'"CPUTemp": "48.31", "SensorTemp": 0}'
DATA_PKT2 = b'{"time": "10:05:13", "date": "2022-11-18", "packet_id": 3, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20602, ' \
            b'"CPUTemp": "48.31", "SensorTemp": "41.79"}'
DATA_PKT3 = b'{"time": "10:06:13", "date": "2022-11-18", "packet_id": 4, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20648, ' \
            b'"CPUTemp": "47.24", "SensorTemp": 0}'
print(DATA_PKT1)


def print_data_file():
    saved_filename = "2022-11-18.csv"
    saved_file_path = os.path.join('..', 'GUI', 'data', saved_filename)
    # print(f"saved file path: {saved_file_path}")
    if os.path.isfile(saved_file_path):
        with open(saved_file_path, 'r') as _file:
            print(_file.read())
    else:
        print("No file yet")


class TestAddDataPacket(unittest.TestCase):
    @freezegun.freeze_time("2022-11-18")
    @mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock, return_value=True)
    def test_add_data_pkt(self, mocked_gui):
        print("start1")
        print_data_file()
        time_stream_data = data_class.TimeStreamData(mocked_gui)
        #TODO: clear any saved data loaded from a file when starting the class
        data_dict = json.loads(DATA_PKT1)
        returned_value = time_stream_data.add_data(data_dict)
        device_data = \
            time_stream_data.positions["position 2"]  # type: GUI.data_class.DeviceData
        print(f"returned value: {returned_value}")
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        print("end1")
        print_data_file()

    @freezegun.freeze_time("2022-11-18")
    @mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock, return_value=True)
    def test_add_2_pkts(self, mocked_gui):
        print("start2")
        print_data_file()
        time_stream_data = data_class.TimeStreamData(mocked_gui)
        # add second packet
        returned_value2 = time_stream_data.add_data(json.loads(DATA_PKT2))
        device_data = \
            time_stream_data.positions["position 2"]  # type: GUI.data_class.DeviceData
        print("test_add_2_pkts")
        print(device_data.time_series)
        print(device_data.oryzanol)
        print("end2")
        print_data_file()
