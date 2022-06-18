# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

from uuid import uuid4


endpoint = "a25h8mlp62407w-ats.iot.ap-southeast-1.amazonaws.com"
topic = "Raw_data"
client_id = "test-" + str(uuid4())

port = 8883

root_ca = "./certs/Amazon-root-CA-1.pem"
cert = "./certs/device.pem.crt"
key = "./certs/private.pem.key"


test_message = [128.4, 132.6]
count = 10