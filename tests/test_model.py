# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

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
from GUI import model

class TestTimeStreamDataStruct(unittest.TestCase):
    def test_models_structure(self):
        self.models = model.Models(["device_1"])
