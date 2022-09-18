# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Some helper functions, usually simple functions that need comprehensive error checking
"""

__author__ = "Kyle Vitatus Lopin"

import datetime
import logging
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
