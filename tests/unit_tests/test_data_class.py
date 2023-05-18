# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Unit tests functions and methods in the data_class file in
the GUI folder
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import os
import sys
import unittest
from unittest import mock

sys.path.append(os.path.join('..', '..', 'GUI'))
# local files
from GUI import data_class


class TestDataClassFunctions(unittest.TestCase):
    def test_convert_csv_row_to_packet_empty(self):
        """ Test that an empty csv row / list will return an empty dict """
        _input = ['', '', '', '', '', '', '', '']
        output = data_class.convert_csv_row_to_packet(_input)
        print(f"output: {output}")
        self.assertEquals(output, {})

    def test_convert_csv_row_to_packet_wrong_position(self):
        """ Test that passing in a position not in the DEVICE list returns
         an empty dict """
        csv_row = "2023-03-07 00:02:53,position 5,15746.0,29.0,40.2,0.0,0"
        _input = csv_row.split(",")
        print(f"input: {_input}")
        output = data_class.convert_csv_row_to_packet(_input)
        print(f"output: {output}")
        self.assertEquals(output, {})

    def test_convert_csv_row_to_packet_1(self):
        """  """
        csv_row = "2023-03-07 00:02:53,position 1,15746.0,29.0,40.2,0.0,0"
        _input = csv_row.split(",")
        print(f"input: {_input}")
        output = data_class.convert_csv_row_to_packet(_input)
        print(f"output: {output}")
        expected = {'packet_id': 0, 'position': 'position 1', 'time': '00:02:53', 'CPUTemp': 40.2,
                    'SensorTemp': 0.0, 'OryConc': 15746.0, 'AV': 29.0}
        self.assertEquals(output, expected)
        # test a line that caused an error
        _input = [' 00:02:37', ' position 2', '-164265.5', '-2', '46.2', '42.9', '1', '']
        output = data_class.convert_csv_row_to_packet(_input)
        print(f"output: {output}")
        expected = {'packet_id': 1, 'position': 'position 2', 'time': '00:02:37', 'CPUTemp': 46.2, 'SensorTemp': 42.9,
                    'OryConc': -164265.5, 'AV': -2.0}
        self.assertEquals(output, expected)

    def test_valid_time(self):
        """ Test that the valid_time function works"""
        output = data_class.extract_time_stamp("bbb")
        self.assertEquals(output, "")
        output = data_class.extract_time_stamp("2023-05-12 10:25:45")
        self.assertEquals(output, "10:25:45")
        output = data_class.extract_time_stamp("13:45:30")
        self.assertEquals(output, "13:45:30")
        output = data_class.extract_time_stamp("2023-05-12")
        self.assertEquals(output, "")

    def test_isint(self):
        """ Test the isint function works """
        self.assertEquals(data_class.isint("1"), True)
        self.assertEquals(data_class.isint("b"), False)
        self.assertEquals(data_class.isint("1.543"), False)

    def test_isint(self):
        """ Test the isfloat function works """
        self.assertEquals(data_class.isfloat("1"), True)
        self.assertEquals(data_class.isfloat("b"), False)
        self.assertEquals(data_class.isfloat("1.543"), True)
