# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Test that the logging of information when running
the TimeStreamData is called
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from datetime import datetime as dt
import logging
import os
import sys
import unittest
from unittest import mock

# local files
sys.path.append(os.path.join('..', 'GUI'))
from GUI import data_class

date = dt.today().strftime("%Y-%m-%d")
print(date)
DATA_PKT1 = {"time": "09:55:22", "date": date, "packet_id": 1,
             "device": "position 2", "mode": "live", "OryConc": -20139,
             "CPUTemp": "48.31", "SensorTemp": 0, "AV": -1}
print(DATA_PKT1)
class TestLoggingTimeStreamData(unittest.TestCase):
    def test_logging(self):
        """ Test that the logging module works for measure the
         time to completion, RAM and CPU usages of the add_data method
         in TimeStreamData"""
        with mock.patch("GUI.main_gui.RBOGUI",
                        new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            logging.debug("Making TimeStreamData now")
            self.tsd = data_class.TimeStreamData(mocked_gui)
            return_code = self.tsd.add_data(DATA_PKT1)
            print(f"return code: {return_code}")
            print(self.tsd.positions)
            print(self.tsd.positions["position 2"].av)
            # logger = logging.Logger()
            # with self.assertLogs(logger, level="DEBUG") as cm:
            #     print(cm.output)
