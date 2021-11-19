# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Classes to hold the data for NIR sensors measuring
oryzanol concentrations on an IoT sensor.
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
from datetime import datetime
import json
import logging
# installed libraries
# import numpy as np
# local files
import global_params

TIME_KEYWORD = "Datetime"
CPUTEMP_KEYWORD = "CPUTemp"
ORYZONAL_KEYWORD = "OryConc"
json_data = open("sensor_settings.json").read()

SENSOR_INFO = json.loads(json_data)
json_data2 = open("master_settings.json").read()
SETTINGS = json.loads(json_data2)
DISPLAY_ROLLING_MEAN = SETTINGS["Rolling avg"]
ROLLING_SAMPLES = SETTINGS["Rolling samples"]
LOG_RAW_DATA = SETTINGS["log data"]  # option to save raw data
FILE_HEADER = ["time", "device", "OryConc", "CPUTemp", "SensorTemp", "packet id"]
RAW_DATA_HEADERS = ["time", "device", "OryConc"]
RAW_DATA_HEADERS.extend([str(i) for i in range(1350, 1651)])


def mean(_list: list):
    sum = 0
    for num in _list:
        sum += int(num)
    return sum/len(_list)


def divide(list1: list, list2: list):
    result = []
    for num1, num2 in zip(list1, list2):
        result.append(int(num1)/int(num2))
    return result


class DeviceData:
    def __init__(self):
        self.time_series = []
        self.packet_ids = []
        self.cpu_temp = []
        self.oryzanol = []
        self.rolling = []
        self.latest_packet_id_recieved = 0
        self.next_packet_to_get = 1
        self.stored_packets = {}
        self._mode = "WAIT"

    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        if mode == "WAIT":
            self._mode = mode
        elif mode == "ASK":
            self._mode = mode
        else:
            print(f"ERROR, incompatible mode {mode}, enter either 'WAIT' or 'ASK'")

    def is_correct_packet(self, pkt):
        print(f" check packet: {pkt['packet id']} and {self.next_packet_to_get}")
        if pkt["packet id"] == self.next_packet_to_get:
            return True
        return False

    def store_packet(self, pkt):
        self.stored_packets[pkt["packet id"]] = pkt

    def add_data_pt(self, time, cpu, ory):
        self.time_series.append(time)
        self.cpu_temp.append(cpu)
        self.oryzanol.append(ory)

    def add_data_list(self, time_list, cpu_list, ory_list):
        self.time_series.extend(time_list)
        self.cpu_temp.extend(cpu_list)
        self.oryzanol.extend(ory_list)

    def get_packet_ids(self):
        return self.packet_id

    def __str__(self):
        _str = f"Time series: {self.time_series}\n"
        _str += f"CPU Temps: {self.cpu_temp}\n"
        _str += f"Oryzanol concentrations: {self.oryzanol}\n"
        return _str


class TimeStreamData:
    def __init__(self, graph):
        print("Init Time Stream Data")
        self.master_graph = graph
        self.root_app = graph.root_app  # this is not pretty
        self.devices = {}
        # this is needed to make the datetime in the data
        self.today = datetime.today()
        today = datetime.today().strftime("%Y-%m-%d")
        self.save_file = f"data/{today}.csv"
        self.make_file(self.save_file, FILE_HEADER)
        if LOG_RAW_DATA:
            self.save_rawdata_file = f"data/{today}_raw_data.csv"
            self.make_file(self.save_rawdata_file, RAW_DATA_HEADERS)

    def add_device(self, device):
        logging.info(f"adding device: {device} to data_class")
        if device not in global_params.DEVICES:
            # see if it was send as position and fix it
            try:
                device = global_params.POSITIONS[device]
            except Exception as error:
                print(f"{device} is not on the list")
        if device in global_params.DEVICES:
            self.devices[device] = DeviceData()
        else:
            print(f"{device} is not on the list, part 2")

    def add_data(self, data_pkt: dict, save_data=True):
        # print(f"got data packet: {data_pkt['packet id']}")
        # print(f"packet keys: {data_pkt.keys()}")
        # print("OryConc" in data_pkt)
        # print(f"got data packet type: {type(data_pkt)}")
        # print("TODO process for AWS difference")
        if "Info" in data_pkt:  # is database information
            device = data_pkt["Info"]["device"]
            time = datetime.strptime(data_pkt[TIME_KEYWORD], "%H:%M:%S").time()
            data_pkt = data_pkt["Info"]
        # else:  # is mqtt data
        #     device = data_pkt["device"]
        #     time = datetime.strptime(data_pkt["time"], "%H:%M:%S").time()

        position = data_pkt["device"]
        device = global_params.POSITIONS[position]

        # device = data_pkt["Info"]["device"]
        # if device is not seen yet, add it to device dict

        # print(f"adding data: {device}")
        # print(self.devices)
        if device not in self.devices:
            self.add_device(device)
        device_data = self.devices[device]  # type: DeviceData
        if "packet id" in data_pkt:
            pkt_id = int(data_pkt["packet id"])
        else:
            print(f"No packet id, abondoning data")
            return

        # if not device_data.is_correct_packet(pkt_id):
        #     print(f"Not correct packet {pkt_id}, looking for {device_data.next_packet_to_get}")
        #     device_data.stored_packets[pkt_id] = data_pkt
        #     if device_data.get_mode() == "WAIT":
        #         device_data.set_mode("ASK")
        #         print("Asking for data")
        #         # this is a hack, idk how to make it better
        #         self.root_app.check_remote_data(device)
        #     return  # don't add data yet

        if "Raw_data" in data_pkt:
            raw_data = data_pkt["Raw_data"]
            # reference_data = np.array(SENSOR_INFO[position]["Ref Intensities"])
            # reference_data = SENSOR_INFO[position]["Ref Intensities"]
            reference_data = SENSOR_INFO["Ref Intensities"]
            reflectance_data = divide(raw_data, reference_data)
            self.master_graph.update_spectrum(reflectance_data, device)
            # self.master_graph.devices[device].spectrum_frame.update(reflectance_data)
        if "CPUTemp" in data_pkt:
            temp = data_pkt["CPUTemp"]
            self.master_graph.update_temp(device, temp)
        if "packet id" in data_pkt:
            device_data.packet_ids.append(int(data_pkt["packet id"]))

        if "OryConc" in data_pkt:
            time = datetime.strptime(data_pkt["time"], "%H:%M:%S").time()
            # print(f"time: {time}")
            time = datetime.combine(self.today, time)
            device_data.time_series.append(time)
            device_data.oryzanol.append(data_pkt["OryConc"])
            # calculate rolling average
            last_samples = device_data.oryzanol[-ROLLING_SAMPLES:]
            # print(last_samples)
            roll_avg = mean(last_samples)
            device_data.rolling.append(roll_avg)
            # print("update master")
            self.master_graph.update(device, device_data.time_series,
                                     device_data.oryzanol,
                                     device_data.rolling)
        if save_data:  # this is live data
            self.save_data(data_pkt)
            self.master_graph.check_in(device)

    def save_data(self, data_pkt):
        # make a string of the data and write it
        data_list = []
        for item in FILE_HEADER:
            if item in data_pkt:
                data_list.append(str(data_pkt[item]))
            else:
                data_list.append("")
        data_list.append('\n')
        # now write a row to the file
        try:
            with open(self.save_file, 'a') as _file:
                _file.write(', '.join(data_list))
        except Exception:
            # do something here to save the list and write later
            pass
        if LOG_RAW_DATA:
            data_list2 = []
            for item in RAW_DATA_HEADERS[:3]:
                # print(f"add item: {item}")
                if item in data_pkt:
                    data_list2.append(str(data_pkt[item]))
                else:  # make a blank entry
                    data_list2.append(", ")
            if "Raw_data" in data_pkt:
                data_list2.extend([str(i) for i in data_pkt["Raw_data"]])
                # print("WRITING RAW data")
                with open(self.save_rawdata_file, 'a') as _file:
                    _file.write(', '.join(data_list2))
                    _file.write("\n")

    def check_missing_packets(self):
        for device in self.devices:
            reads_in = self.devices[device].get_packet_id()
            print(f"device: {device} has packets: {reads_in}")

    def get_missing_packets(self, device):
        print(f"updating packets with remote data: {device}")
        missing_ids = []
        device_data = self.devices[device]
        for i in range(1, device_data.latest_packet_id+1):
            print(f"comparing {i} in {device_data.packet_ids} or {device_data.stored_packets}")
            if i not in device_data.packet_ids:
                if i not in device_data.stored_packets:
                    missing_ids.append(i)
        return missing_ids
        # self.check_prev_reads(device, self.devices[device].latest_packet_id)

    def check_prev_reads_dep(self, device, num_packets):
        print(f"Updating packets for {num_packets} packets")
        print(f"{self.devices}")
        print(f"for device: {device}")
        print(f"we have packets: {self.devices[device].packet_ids}")

        for i in range(1, num_packets+1):
            print(f"Comparing {i} in {self.devices[device].packet_ids}")
            print(f"{type(i)} {type(self.devices[device].packet_ids)} {type(self.devices[device].packet_ids[0])}")
            if i in self.devices[device].packet_ids:
                print(f"We already have packet: {i}")
            else:
                print(f"getting packet: {i}")

    def update_latest_packet_id(self, device, pkt_num):
        # this is the first method to see the device so add it to devices
        if device not in self.devices:
            self.add_device(device)
        self.devices[device].latest_packet_id = pkt_num

    # def add_mqtt_data(self, data_pkt):
    #     device = data_pkt["device"]

    def add_db_data(self, data_pkt):
        device = data_pkt["Info"]["device"]
        # if device is not seen yet, add it to device dict
        if device not in self.devices:
            self.add_device(device)
            # self.devices[device] = DeviceData()
            self.master_graph.add_device(device)

        time = datetime.datetime.strptime(data_pkt[TIME_KEYWORD], "%H:%M:%S").time()
        today = datetime.date.today()
        full_time = datetime.datetime.combine(today, time)
        print(time)
        print(type(data_pkt["Info"][CPUTEMP_KEYWORD]))
        self.devices[device].add_data_pt(full_time,
                                         float(data_pkt["Info"][CPUTEMP_KEYWORD]),
                                         float(data_pkt["Info"][ORYZONAL_KEYWORD]))

    @staticmethod
    def make_file(filepath, header):
        try:
            with open(filepath, 'x') as _file:
                # use 'x' to try to make the file, if it exists
                # it will raise an error and just pass
                header.append('\n')
                _file.write(', '.join(header))
        except Exception:
            pass

    def __str__(self):
        if not self.devices:
            _str = "No device"
        else:
            _str = ""
            for device in self.devices:
                _str += f"{device} properties:"
                _str += f"{self.devices[device]}\n"
        return _str


if __name__ == "__main__":
    r = divide([1, 2, 3], [4, 5, 6])
    print(r)
