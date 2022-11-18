# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Some helper functions, usually simple functions that need comprehensive error checking
"""

__author__ = "Kyle Vitatus Lopin"

import datetime
import json
import logging
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
logger = logging.getLogger(__name__)


TIME_KEYWORD = "Datetime"


def get_packet_data(pkt):
    try:
        packet_date = pkt["date"]
        packet_datetime = datetime.strptime(packet_date, "%Y-%m-%d").date()
    except Exception as e:
        return None


def check_database_info(data_pkt):
    if "Info" in data_pkt:  # is database information
        time = data_pkt[TIME_KEYWORD]
        data_pkt = data_pkt["Info"]
        data_pkt["time"] = time
        return data_pkt  # return new formatted data packet
    return data_pkt  # no change


def make_model_json(device):
    """
    Make the model.json file for a device, ie "device_1" to
    put in the sensor program from the
    :param device: string, "device_1", "device_2" etc to get
    :return:
    """
    with open(os.path.join(__location__, "new_models.json"), "r") as _file:
        data = json.load(_file)
    print(data)
    device_data = data[device]
    print(device_data)
    with open(os.path.join(__location__, "models.json"), "w") as _file:
        json.dump(device_data, _file)


if __name__ == "__main__":
    make_model_json("device_1")
