# Copyright (c) 2022-23 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import os
import sys
import unittest
from unittest import mock

# installed libraries
import freezegun

# local files
# sys.path.append(os.path.join('..', 'GUI'))  # in context
from context import GUI  # add the app files to teh path
from GUI import data_class


LOAD_DATE = "2023-03-07"


class TestTimeStreamDataStruct(unittest.TestCase):
    def test_av_in_structure(self):
        with mock.patch("GUI.main_gui.RBOGUI",
                        new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)
            print(self.tsd.positions)
            for device, data in self.tsd.positions.items():
                print(f"device: {device}")
                print(data.use_av)


@freezegun.freeze_time(LOAD_DATE)
class LoadData(unittest.TestCase):
    """ Load the data for current day for testing, not unittesting """
    def test_today(self):
        with mock.patch("GUI.main_gui.RBOGUI",
                        new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)
            print(self.tsd.positions)
            for position in self.tsd.positions:
                print(f"position: {position}")
                print(self.tsd.positions[position].av)


@freezegun.freeze_time(LOAD_DATE)
class LoadDataDateTimeFormat(unittest.TestCase):
    def test_format(self):
        """ Test the program will load data with the time column
        being datetime, not just time, load the time as just time
        but re-save the summary data """
        with mock.patch("GUI.main_gui.RBOGUI",
                        new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)
            print(self.tsd.positions)
            print('====')
            for position in self.tsd.positions:
                print(f"position: {position}")
                print(self.tsd.positions[position].time_series)


