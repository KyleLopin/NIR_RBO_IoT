# Copyright (c) 2022-23 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import os
import sys
import unittest
from unittest import mock

# local files
sys.path.append(os.path.join('..', 'GUI'))
from GUI import data_class


class TestTimeStreamDataStruct(unittest.TestCase):
    def test_av_in_structure(self):
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)
            print(self.tsd.positions)
            for device, data in self.tsd.positions.items():
                print(f"device: {device}")
                print(data.use_av)


class LoadTodayData(unittest.TestCase):
    """ Load the data for current day for testing, not unittesting """
    def test_today(self):
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)
            print(self.tsd.positions)
            for position in self.tsd.positions:
                print(f"position: {position}")
                print(self.tsd.positions[position].av)
