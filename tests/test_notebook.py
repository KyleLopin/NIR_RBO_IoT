# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Test class and methods in the notebook.py file
"""

__author__ = "Kyle Vitautas Lopin"

# local files
from datetime import datetime
import os
import sys
from tkinter import Tk
import unittest
from unittest.mock import patch

# local files
from context import GUI
from GUI import notebook


class TestNotebookMethods(unittest.TestCase):
    def setUp(self) -> None:
        mock_gui = Tk()
        self.notebook = notebook.Notebook(mock_gui)

    def test_update_temp_mask(self):
        """ This is super sticky problem so don't let this fail """
        # actual data that failed
        self.notebook.update_temp([datetime(2023, 5, 24, 9, 55, 22)],
                                  [48.31], [0.0], "position 2")
        self.notebook.update_temp([datetime(2023, 5, 24, 9, 55, 22),
                                   datetime(2023, 5, 24, 9, 56, 22)],
                                  [48.31, 35.4], [0.0, 10], "position 2")
