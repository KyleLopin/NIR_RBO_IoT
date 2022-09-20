# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard liberaries
from datetime import datetime
import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
DATA_FOLDER = os.path.join(__location__, "data")


def get_data_needed(position, remote_data: list):
    data_needed = []
    for filename, packets_in_remote in remote_data:
        # print(data)
        # filename, packets = data[0][0], data[0][1]
        filepath = os.path.join(DATA_FOLDER, filename)
        if os.path.isfile(filepath):
            pkts = get_packets(position, filepath, packets_in_remote)
            pkts_needed = find_missing_packets(pkts, packets_in_remote)
            print(f"pkts needed: {pkts_needed}")
            data_needed.append([filename, pkts_needed])
    print(data_needed)
    return data_needed


def find_missing_packets(pkts_rx, pkts_in_remote):
    pkts_needed = []
    for i in range(int(pkts_in_remote)):
        if i not in pkts_rx:
            pkts_needed.append(i)
    return pkts_needed


def get_packets(position, file, num_packets):
    packets = []
    device_index = 0
    packet_index = 0
    with open(file, 'r') as _file:
        for line in _file.readlines():
            split_line = line.split(",")
            if "device_number" in line:  # first line
                for i, item in enumerate(split_line):
                    if "device_number" in item:
                        device_index = i
                    elif "packet" in item:
                        packet_index = i
            else:
                device = split_line[device_index]
                if position in device:
                    packets.append(int(split_line[packet_index]))
    return packets


def find_data_files():
    today = datetime.today().strftime("%Y-%m-%d")
    files = []
    for file in os.listdir(DATA_FOLDER):
        if today not in file:
            files.append(file)
    return files


if __name__ == "__main__":
    get_data_needed("position 1", [["2021-12-06.csv", "2000"]])
