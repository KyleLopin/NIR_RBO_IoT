# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Basic tests to see if the logger is working correctly,
for tests the log file should be in the NIR_ROB/tests/log folder
but production logs are in NIR_ROB/GUI/log folder
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from datetime import datetime
from importlib import reload
import logging
import os
import sys
import unittest

sys.path.append(os.path.join('..', '..', 'GUI'))

# logger = logging.getLogger('my_logger')
# logger.setLevel(logging.DEBUG)
# today = datetime.today().strftime("%Y-%m-%d")
# # put logs in the log folder for the tests, not unit_tests
# test_log_handler = logging.FileHandler(f'../log/{today}.log')
# test_log_handler.setLevel(logging.DEBUG)
# format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(filename)-15s - line: %(lineno)d - %(message)s')
# test_log_handler.setFormatter(format)
# logger.addHandler(test_log_handler)


class TestLogs(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)
        today = datetime.today().strftime("%Y-%m-%d")
        # put logs in the log folder for the tests, not unit_tests
        test_log_handler = logging.FileHandler(f'../log/{today}.log')
        test_log_handler.setLevel(logging.DEBUG)
        format = logging.Formatter(
            '%(asctime)s - %(levelname)-8s - %(filename)-15s - line: %(lineno)d - %(message)s')
        test_log_handler.setFormatter(format)
        self.logger.addHandler(test_log_handler)

    def test_log_main_starts(self):
        pass  # does not work because unittests only import modules once
        # fill this end later
        # with self.assertLogs(self.logger, level="DEBUG") as captured_logs:
        #     from GUI import main_gui
        #
        # print(dir(captured_logs))
        # all_records = []
        # for record in captured_logs.records:
        #     all_records.append(record.getMessage())
        #     print(f"name: {record.name}")
        #     print(record.getMessage())
        # self.assertIn("Start of main_gui", all_records)

