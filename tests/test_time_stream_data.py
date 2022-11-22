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
TEST_DATE = "2022-11-18"

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


def get_data_file() -> str:
    saved_file_path = os.path.join('..', 'GUI', 'data', f"{TEST_DATE}.csv")
    if os.path.isfile(saved_file_path):
        with open(saved_file_path, 'r') as _file:
            return _file.read()
    else:
        return "No file yet"


@freezegun.freeze_time(TEST_DATE)
class TestAddDataPacket(unittest.TestCase):
    saved_filename = os.path.join('..', 'GUI', 'data', f"{TEST_DATE}.csv")

    def setUp(self) -> None:
        """ Delete any saved filed for the simulated test data """
        if os.path.exists(self.saved_filename):
            os.remove(self.saved_filename)
        self.mocked_gui = 1  #TODO: pass the patch here

    @mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock, return_value=True)
    def test_add_data_pkt(self, mocked_gui):
        self.assertEqual(get_data_file(), "No file yet",
                         msg="File is not being deleted between tests correctly")
        time_stream_data = data_class.TimeStreamData(mocked_gui)
        data_dict = json.loads(DATA_PKT1)
        returned_value = time_stream_data.add_data(data_dict)
        device_data = \
            time_stream_data.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        print("end1")
        print(get_data_file())

    @mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock, return_value=True)
    def test_add_2_pkts(self, mocked_gui):
        """
        Test that adding 2 packets creates the correct device data
        time_stream and oryzanol attribute lists.  Use the test_add_data_pkt()
        to add the first packet again.
        Args:
            mocked_gui:

        """
        self.test_add_data_pkt()
        time_stream_data = data_class.TimeStreamData(mocked_gui)
        # add second packet
        returned_value = time_stream_data.add_data(json.loads(DATA_PKT2))
        device_data = \
            time_stream_data.positions["position 2"]  # type: GUI.data_class.DeviceData
        print("test_add_2_pkts")
        print(device_data.time_series)
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22),
                              dt.datetime(2022, 11, 18, 10, 5, 13)],
                             msg="add_data is not saving a second time_series "
                                 "correctly")
        print(device_data.oryzanol)
        self.assertListEqual(device_data.oryzanol, [-20139.0, -20602.0],
                             msg="add_data is not saving a second oryzanol "
                                 "data packet correctly")
        print("end2")
        print(get_data_file())
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code"
                             "for the second packet")


    @mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock, return_value=True)
    def test_make_save_file(self, mocked_gui):
        # TODO: move this to other unittest file
        data_class.TimeStreamData(mocked_gui)
        self.assertEqual(get_data_file(), "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n",
                         msg="saved data file not being created correctly")
