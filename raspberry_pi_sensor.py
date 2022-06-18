# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import json

# installed libraries
import aws_conn

# local files
import device_codes



class NIRPiSensor:
    def __init__(self):
        self.aws_connection = aws_conn.aws_iot_mqtt()
        self.aws_connection.wait_for_connect()
        print("Connected")
        # pass connection to nirone
        # nirone =



    def disconnect_mqtt(self):
        self.aws_conn.disconnect()
