# Copyright (c) 2022-3 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Allow the test files to import files from the
source GUI folder. Needed in all sub test folders for
the PyCharm unittest to be run from the tabs
"""

__author__ = "Kyle Vitatus Lopin"


import os
import sys

sys.path.append(os.path.join('..', 'GUI'))
import GUI