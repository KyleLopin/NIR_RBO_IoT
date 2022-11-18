# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import datetime
import json
import os
import sys
import unittest
from unittest import mock

sys.path.append(os.path.join('..', 'GUI'))
# local files
import data_class

DATA_PKT1 = b'{"time": "09:55:22", "date": "2022-11-18", "packet_id": 1, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20139, ' \
            b'"CPUTemp": "48.31", "SensorTemp": 0}'
DATA_PKT2 = b'{"time": "10:05:13", "date": "2022-11-18", "packet_id": 3, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20602, ' \
            b'"CPUTemp": "48.31", "SensorTemp": "41.79"}'
DATA_PKT3 = b'{"time": "10:06:13", "date": "2022-11-18", "packet_id": 4, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20648, ' \
            b'"CPUTemp": "47.24", "SensorTemp": 0}'


class TestAddDataPacket(unittest.TestCase):
    def test_add_data_pkt(self):
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            time_stream_data = data_class.TimeStreamData(mocked_gui)
        print(f"test: {time_stream_data}")
        #TODO: clear any saved data loaded from a file when starting the class
        # data_dict = ast.literal_eval(DATA_PKT1)
        data_dict = json.loads(DATA_PKT1)
        returned_value = time_stream_data.add_data(data_dict)
        device_data = \
            time_stream_data.positions["position 2"]  # type: GUI.data_class.DeviceData

        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [datetime.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        # add second packet
        returned_value2 = time_stream_data.add_data(json.loads(DATA_PKT2))
        print(device_data.time_series)
        print(device_data.oryzanol)
