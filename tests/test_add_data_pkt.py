# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautus Lopin"

import unittest

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
    def
