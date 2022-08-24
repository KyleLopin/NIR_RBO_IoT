# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import unittest
from unittest import mock
from datetime import datetime
import os
import shutil
import sys
# fix the imports of the GUI files
sys.path.append('/Users/kylesmac/PycharmProjects/NIR_ROB/GUI')
# local files
# import GUI
# from GUI import data_class
import GUI.data_class as data_class
from GUI.main_gui import RBOGUI  # for mock
# my_path = os.path.os.path.dirname(os.path.abspath(__file__))
# print(f"my path: {my_path}")
# sys.path.insert(0, my_path+'/../')
# from .context import GUI

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def copy_data_test_file():
    # make a file to simulate the data file
    today = datetime.today().strftime("%Y-%m-%d")
    print(today)
    os.chdir('..')
    new_data_file = os.path.join(os.getcwd(), f"GUI/data/{today}.csv")
    template_file = os.path.join(__location__, "template.csv")
    print(new_data_file)
    print(template_file)
    shutil.copyfile(template_file, new_data_file)

class TestDataClass(unittest.TestCase):
    @mock.patch('GUI.main_gui.RBOGUI')
    def test_load_file(self, mocked_gui):
        """ Test if the current date file is loaded
         correctly in the data_class"""
        copy_data_test_file()  # copy file to test with proper name
        data_class.TimeStreamData(mocked_gui)


if __name__ == "__main__":
    # copy_data_test_file()  # copy file to test with proper name
    unittest.main()
