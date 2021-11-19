# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Class to read and write from a file in a thread save manner
"""

__author__ = "Kyle Vitatus Lopin"


# standard libraries
import queue
import threading



class FileWriter(threading.Thread):
    def __init__(self, filename: str):
        threading.Thread.__init__(self)
        self.filename = filename
        self.lock = threading.Lock()
        self.write_queue = queue.Queue()
        self.read_queue = queue.Queue()

    def write_line_to_file(self, data):
        """
        Take in a string, or list to combine into a string,

        :param data:
        :return:
        """
        if type(data) is list:
            data = [", ".join(data)]
        elif type(data) is not str:
            raise TypeError("data must list or string")
        self.write_queue.put(data)

    def _write_file(self, data_str):
        """
        Take a string and write it to a file in a thread save manner
        :param data_str: str to write to the fike
        :return:
        """
        self.lock.
        with open(self.filename, 'w+') as _file:

