# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Classes to hold the data for NIR sensors measuring
oryzanol concentrations on an IoT sensor.
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import csv
from datetime import datetime
import json
import logging
import os
import shutil
import tkinter as tk  # typehinting

# installed libraries
import numpy as np
# local files
import global_params
import model

MAX_DATA_PTS = 240
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

TIME_KEYWORD = "Datetime"
CPUTEMP_KEYWORD = "CPUTemp"
ORYZONAL_KEYWORD = "OryConc"
json_data = open(os.path.join(__location__, "sensor_settings.json")).read()
SENSOR_INFO = json.loads(json_data)
DEVICES = list(global_params.DEVICES.keys())
POSITIONS = list(global_params.POSITIONS.keys())
json_data = open(os.path.join(__location__, "new_models.json")).read()
MODEL_INFO = json.loads(json_data)
USE_LOCAL_MODEL = True
#
#
json_data2 = open(os.path.join(__location__, "master_settings.json")).read()
SETTINGS = json.loads(json_data2)
DISPLAY_ROLLING_MEAN = SETTINGS["Rolling avg"]
rolling_samples = SETTINGS["Rolling samples"]
LOG_RAW_DATA = SETTINGS["log data"]  # option to save raw data
FILE_HEADER = ["time", "position", "OryConc", "AV", "CPUTemp", "SensorTemp", "packet_id"]
FILE_HEADER_TO_SAVE = ["time", "device", "OryConc", "AV", "CPUTemp", "SensorTemp", "packet_id"]

DATA_PACKET_KEYS = ["time", "device", "CPUTemp", "SensorTemp", "packet_id"]
SAVED_DATA_KEYS = DATA_PACKET_KEYS.extend(["AV", "OryConc"])
RAW_DATA_HEADERS = ["time", "device", "packet_id"]
RAW_DATA_HEADERS.extend([str(i) for i in range(1350, 1651)])

indices = dict()
for header in FILE_HEADER:
    indices[header] = FILE_HEADER.index(header)


def mean(_list: list):
    sum = 0
    for num in _list:
        sum += int(num)
    return sum / len(_list)


def divide(list1: list, list2: list):
    result = []
    for num1, num2 in zip(list1, list2):
        result.append(float(num1) / float(num2))
    return result


def isfloat(str_to_test: str) -> bool:
    try:
        float(str_to_test)
        return True
    except:
        return False


def isint(str_to_test: str) -> bool:
    try:
        int(str_to_test)
        return True
    except:
        return False


# TODO: convert DataPacket class to set of functions
def convert_csv_row_to_packet(csv_row):
    pkt = {}
    if isint(csv_row[indices["packet_id"]]):
        pkt["packet_id"] = int(csv_row[indices["packet_id"]])
    for obj in ["time", "position"]:
        pkt[obj] = csv_row[indices[obj]].strip()
    for obj in ["CPUTemp", "SensorTemp", "OryConc"]:
        if isfloat(csv_row[indices[obj]]):
            pkt[obj] = float(csv_row[indices[obj]])
    return pkt


class DataPacket:
    def __init__(self, date=None, time=None, packet_id=None,
                 device=None, raw_data=None, ory_conc=None,
                 av_value=None, cpu_temp=None,
                 sensor_temp=None, mode=None, packet=None,
                 data_line=None):
        self.packet = dict()
        self.raw_data = raw_data
        self.date = date
        self.cpu_temp = cpu_temp
        self.sensor_temp = sensor_temp
        self.packet = packet
        self.ory_conc = ory_conc
        self.av = av_value
        self.mode = mode

        if packet:
            self.packet = packet
            self.time = packet["time"]
            self.device = packet["device"]
            self.date = packet["date"]
            self.packet_id = packet["packet_id"]
            if "Raw_data" in packet:
                self.raw_data = packet["Raw_data"]
            if "CPUTemp" in packet:
                self.cpu_temp = packet["CPUTemp"]
            if "SensorTemp" in packet:
                self.sensor_temp = packet["SensorTemp"]
            print(f"packet made1")
        elif packet_id is not None:  # can be 0 and legit
            self.time = time
            self.device = device
            self.packet_id = packet_id
            # the rest are assigned above
            self.make_packet()
            print(f"packet made2")
        elif data_line:
            self.parse_line(data_line)
            print(f"packet made3")
        else:
            raise Exception("Wrong input to DataClass")

    def make_packet(self):
        self.packet = {"time": self.time,
                       "packet_id": self.packet_id,
                       "device": self.device,
                       "mode": self.mode,
                       "OryConc": self.ory_conc,
                       "AV": self.av,
                       "CPUTemp": self.cpu_temp,
                       "SensorTemp": self.sensor_temp}
        print(f"packet111: {self.packet}")
        # this packet is send through json so truncate the raw data floats
        # TODO: is this worth it?

    def parse_line(self, csv_line):
        print(f"parsing line {csv_line}")
        split_line = csv_line.split(",")
        print(f"line split: {split_line}")
        self.packet_id = int(split_line[indices["packet_id"]])
        self.time = split_line[indices["time"]].lstrip()
        self.device = split_line[indices["device"]]
        self.ory_conc = float(split_line[indices["OryConc"]])
        self.av = float(split_line[indices["AV"]])
        self.cpu_temp = float(split_line[indices["CPUTemp"]])
        self.sensor_temp = float(split_line[indices["SensorTemp"]])
        self.raw_data = split_line[len(FILE_HEADER):]
        self.mode = "saved"
        self.make_packet()

    def get_csv_line(self):
        _list = []
        for item in FILE_HEADER[:len(FILE_HEADER)]:
            _list.append(self.packet[item])
        _list.extend(self.packet["Raw_data"])
        csv_str = str(_list).replace("'", "").replace("[", "").replace("]", "\n").encode('utf-8')
        return csv_str


class DeviceData:
    def __init__(self):
        self.time_series = []
        self.packet_ids = []
        self.cpu_temp = []
        self.sensor_temp = []
        self.oryzanol = []
        self.ory_rolling = []
        self.av = []
        self.av_rolling = []

        self.today = datetime.today()
        self.rolling_samples = rolling_samples
        self.ask_for_missing_packets = False
        self.last_packet_id = -1
        self.next_packet_to_get = 0
        self.lost_pkt_ptr = None  # use this to find missing pkts
        self._mode = "WAIT"
        self.model_checked = False
        self.settings_checked = False

    def save_summary_data(self, csv_writer: csv.writer, position: str):
        print(f"save position summary data")
        for i in range(len(self.packet_ids)):
            # make row to write
            print(i)
            if len(self.av) > 0:
                row = [self.time_series[i].strftime("%H:%M:%S"),
                       position, self.oryzanol[i],
                       self.av[i], self.cpu_temp[i],
                       self.sensor_temp[i], self.packet_ids[i]]
            else:
                row = [self.time_series[i].strftime("%H:%M:%S"),
                       position, self.oryzanol[i],
                       '', self.cpu_temp[i],
                       self.sensor_temp[i], self.packet_ids[i]]
            # print(row)
            csv_writer.writerow(row)

    def update_date(self, date):
        self.today = datetime.today()
        self.time_series = []
        self.packet_ids = []
        self.cpu_temp = []
        self.sensor_temp = []
        self.oryzanol = []
        self.ory_rolling = []
        self.av = []
        self.av_rolling = []
        self.ask_for_missing_packets = False
        self.last_packet_id = -1
        self.next_packet_to_get = 0
        self.lost_pkt_ptr = None  # use this to find missing pkts

    def add_data_pkt(self, data_pkt, models):
        print("add data pkt")
        insert_idx = self.check_pkt_id_get_insert_idx(data_pkt)
        if insert_idx == None:
            return  # no pkt id, or one already received
        # print(f"sort idx: {insert_idx}, len packet id: {len(self.packet_ids)}")
        if "AV" in data_pkt:
            self.av.insert(insert_idx, float(data_pkt["AV"]))
            print(f"adding av: {insert_idx}, {float(data_pkt['AV'])}, {self.av}")
        print(data_pkt)
        if "device" in data_pkt:  # this is the code in the sensors still
            position = data_pkt["device"].strip()
        elif "position" in data_pkt:  # trying to move all code to here
            position = data_pkt["position"]
        else:
            raise KeyError("data packet has to have 'position' or 'device' in it")

        device = global_params.POSITIONS[position]

        if USE_LOCAL_MODEL and ("Raw_data" in data_pkt):
            raw_data = [float(x) for x in data_pkt["Raw_data"]]
            ory_conc = models.fit(raw_data, device)
            data_pkt["OryConc"] = ory_conc
            if position == "position 1":
                print(f"making AV values, len av_values: {len(self.av)}, {len(self.time_series)}")

                av_value = models.fit(raw_data, "AV")
                data_pkt["AV"] = av_value
                # print(insert_idx, av_value, device_data.av)
                self.av.insert(insert_idx, av_value)
                self.av_rolling = self.rolling_avg(self.av)

        if "CPUTemp" in data_pkt:
            temp = float(data_pkt["CPUTemp"])
            self.cpu_temp.insert(insert_idx, temp)
        else:
            self.cpu_temp.insert(insert_idx, np.nan)
        if "SensorTemp" in data_pkt:
            sensor_temp = float(data_pkt["SensorTemp"])
            self.sensor_temp.insert(insert_idx, sensor_temp)
        else:
            self.sensor_temp.insert(insert_idx, np.nan)

        self.packet_ids.insert(insert_idx, int(data_pkt["packet_id"]))
        time = datetime.strptime(data_pkt["time"], "%H:%M:%S").time()
        time = datetime.combine(self.today, time)
        self.time_series.insert(insert_idx, time)
        self.oryzanol.insert(insert_idx, float(data_pkt["OryConc"]))
        self.ory_rolling = self.rolling_avg(self.oryzanol)
        return data_pkt

    def resize_data(self):
        self.time_series = self.time_series[-MAX_DATA_PTS:]
        self.packet_ids = self.packet_ids[-MAX_DATA_PTS:]
        self.cpu_temp = self.cpu_temp[-MAX_DATA_PTS:]
        self.sensor_temp = self.sensor_temp[-MAX_DATA_PTS:]
        self.oryzanol = self.oryzanol[-MAX_DATA_PTS:]
        self.ory_rolling = self.ory_rolling[-MAX_DATA_PTS:]
        self.av = self.av[-MAX_DATA_PTS:]
        self.av_rolling = self.av_rolling[-MAX_DATA_PTS:]

    def check_pkt_id_get_insert_idx(self, data_pkt):
        """ Check if the packet id is unique and
        return the index to insert the data in the array if so """
        # print(f"check pkt: {data_pkt}")
        if "packet_id" in data_pkt:
            _pkt_id = int(data_pkt["packet_id"])
            print(f"got packet_id--: {_pkt_id}")
        else:
            # print(f"No packet id, abondoning data")
            return None
        _sort_idx = np.searchsorted(np.array(self.packet_ids), _pkt_id)
        #         print(f"{_pkt_id in self.packet_ids}, pkt ids: {self.packet_ids}")
        if _pkt_id in self.packet_ids:
            print(f"Already recieved pkt id: {_pkt_id}")
            return None  # this packet id is already present
        # print(f"sort idx: {_sort_idx}, len packet id: {len(self.packet_ids)}")
        mode = None
        if "mode" in data_pkt:
            mode = data_pkt["mode"]
        #         print(f"ask for check: mode: {mode}, sort idx: {_sort_idx}, pkt: {_pkt_id}")
        if mode != "saved" and (_sort_idx < _pkt_id):
            self.ask_for_missing_packets = True
        return _sort_idx

    def rolling_avg(self, _list):
        _rolling_avg = []
        for i in range(1, len(_list) + 1):
            if (i - self.rolling_samples) > 0:
                avg = sum(_list[i - self.rolling_samples:i]) / rolling_samples
            else:
                avg = sum(_list[:i]) / i
            _rolling_avg.append(avg)
        return _rolling_avg


class TimeStreamData:
    def __init__(self, root_app):
        print("Init Time Stream Data")
        self.master_graph = root_app.graphs
        self.connection = None
        devices = DEVICES[:]  # copy to append to it
        devices.append("AV")
        self.models = model.Models(devices)
        # this is not pretty
        self.root_app = root_app  # type: tk.Tk
        self.update_after = None
        self.positions = {}
        # this is needed to make the datetime in the data
        self.today = datetime.today().strftime("%Y-%m-%d")
        # flag to prevent repeately asking for the same data
        self.already_asked_for_data = False
        self.make_save_files()

    def make_save_files(self):
        # check if there is already a file with today's data
        today = datetime.today().strftime("%Y-%m-%d")
        data_path = os.path.join(__location__, "data")
        self.save_file = os.path.join(data_path, f"{today}.csv")
        self.save_raw_data_file = os.path.join(data_path, f"{today}_raw_data.csv")
        if os.path.isfile(self.save_file):
            # file exists so load it
            print("loading previous data")
            self.load_previous_data()
            # resave the data to sort the data if out of order packets were recieved
            print("done loading previous data, resave the summary data=========>")
            self.save_summary_data()
            print("done saving summary data===============================>")
        else:  # no file so make a new one
            self.make_file(self.save_file, FILE_HEADER)
        if LOG_RAW_DATA and not os.path.isfile(self.save_raw_data_file):
            self.make_file(self.save_raw_data_file, RAW_DATA_HEADERS)

    def load_previous_data(self):
        print(f"load file: {self.save_file}")
        with open(self.save_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count != 0 and len(row)>=7:
                    # print(f"load row: {row}")
                    self.add_csv_data(row)
                line_count += 1

    def save_summary_data(self):
        print(f"saving data: {self.positions}")
        with open('sorted_file.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            # write header
            writer.writerow(FILE_HEADER)
            for position in self.positions:
                print(f"saving positions: {position}")
                self.positions[position].save_summary_data(writer, position)
        # os.replace("sorted_file.csv", self.save_file)
        shutil.copyfile("sorted_file.csv", self.save_file)

    def update_date(self, date):
        self.make_save_files()

    def add_connection(self, conn):
        self.connection = conn

    def add_device(self, position):
        logging.info(f"adding device: {position} to data_class")
        print(f"adding device: {position} to data_class")
        if position not in global_params.POSITIONS:
            # see if it was send as position and fix it
            try:
                position = global_params.DEVICES[position]
            except Exception as error:
                print(f"{position} is not on the list")
        if position in global_params.POSITIONS:
            self.positions[position] = DeviceData()
        else:
            print(f"{position} is not on the list, part 2")

    def add_csv_data(self, csv_row):
        """ Add data from a csv row, this will be saved data """
        # position = csv_row[indices["position"]].strip()
        data_pkt = convert_csv_row_to_packet(csv_row)
        position = data_pkt["position"]
        if position:
            if position in POSITIONS and position not in self.positions:
                self.add_device(position)
            device_data = self.positions[position]
            device_data.add_data_pkt(data_pkt, self.models)

    def add_data(self, data_pkt: dict, save_data=True):
        # TODO: fix this, its a mess
        if "Info" in data_pkt:  # is database information
            device = data_pkt["Info"]["device"]
            # time = datetime.strptime(data_pkt[TIME_KEYWORD], "%H:%M:%S").time()
            time = data_pkt[TIME_KEYWORD]
            data_pkt = data_pkt["Info"]
            data_pkt["time"] = time
        position = data_pkt["device"].strip()
        device = global_params.POSITIONS[position]
        # print(f"got data from device: {device}")
        # print(data_pkt)
        if position not in self.positions:
            self.add_device(position)
        # print(f"======: pkt {device_data.last_packet_id}")
        # print(self.positions)
        device_data = self.positions[position]  # type: DeviceData

        # check if date has changed
        device_date = device_data.today.date()
        print('dates: ', device_date, datetime.today().date())
        if device_date != datetime.today().date():
            print("This is a new day")
            self.update_date(None)  # the date is depricated
            device_data.update_date(None)

        data_pkt = device_data.add_data_pkt(data_pkt, self.models)
        device_data.resize_data()
        if not data_pkt:
            return
        print(f"ask 2: {self.already_asked_for_data}")
        if data_pkt and device_data.ask_for_missing_packets and \
                not self.already_asked_for_data:  # this is not data loaded from file
            # or the sensor is not currently sending saved data
            self.already_asked_for_data = True
            self.root_app.after(5*60000, self.clear_ask_for_data_flag)
            missing_pkt = self.find_next_missing_pkts(device_data, int(data_pkt["packet_id"]))
            print(f"ask for packet2: {missing_pkt} from device: {device}")
            
            self.connection.ask_for_stored_data(device, missing_pkt)
            device_data.ask_for_missing_packets = False

        if "Raw_data" in data_pkt and save_data:
            self.master_graph.update_spectrum(data_pkt["Raw_data"], device)

        if not self.update_after:
            self.update_after = self.root_app.after(500, lambda: self.update_graph(position))

        if save_data:  # this is live data
            # TODO: update the ory conc value in this
            print(f"saving data: {data_pkt['packet_id']}")
            self.save_data(data_pkt)
            self.root_app.info.check_in(position)
            # self.master_graph.update_temp(device, temp, "CPU")
            self.root_app.info.update_temp(data_pkt, position)

    def update_rolling_samples(self, n_samples):
        try:
            self.rolling_samples = int(n_samples)
        except TypeError:  # just pass if something weird was passed in
            return
        for device in self.positions:
            device_data = self.positions[device]
            new_rolling_data = self.rolling_avg(device_data.oryzanol)
            self.master_graph.update_roll(device, new_rolling_data)

    def update_graph(self, position):
        print("Updating graph")
        device_data = self.positions[position]  # type: DeviceData
        self.master_graph.update(position, device_data)
        self.update_after = None

    def find_next_missing_pkts(self, device_data, last_pkt_id):
        print(f"finding missing packet: {device_data.packet_ids}, {len(device_data.packet_ids)}")
        missing_pkts = []
        for i in range(last_pkt_id):
            if i not in device_data.packet_ids:
                missing_pkts.append(i)
        return missing_pkts

    def save_data(self, data_pkt):
        # make a string of the data and write it
        data_list = []

        print(f"saving packet: {data_pkt}")
        for item in FILE_HEADER_TO_SAVE:
            print(f"item: {item}")
            if item in data_pkt:
                if type(data_pkt[item]) is float:
                    data_list.append(f"{data_pkt[item]:.1f}")
                else:
                    data_list.append(f"{data_pkt[item]}")
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
                print(f"add item: {item}")
                if item in data_pkt:
                    data_list2.append(str(data_pkt[item]))
                else:  # make a blank entry
                    data_list2.append(", ")
            if "Raw_data" in data_pkt:
                data_list2.extend([str(i) for i in data_pkt["Raw_data"]])
                # print("WRITING RAW data")
                with open(self.save_raw_data_file, 'a') as _file:
                    _file.write(', '.join(data_list2))
                    # print("last data list item", data_list2[-1])
                    if "\n" not in data_list2[-1]:
                        _file.write("\n")

    def check_missing_packets(self, device, pkts_sent):
        # look for missing packets
        print("time: ", datetime.now().strftime("%H:%M:%S"))
        print(f"looking for missing packets for {device}")
        device_data = self.positions[device]
        print(f"device packets: {len(device_data.packet_ids)}, {device_data.packet_ids}")
        if len(device_data.packet_ids) != 0:
            missing_pkt = self.find_next_missing_pkts(self.positions[device], pkts_sent)
        else:  # first connected, ask for data up till now
            missing_pkt = [i for i in range(pkts_sent)]
        print(f"going to ask for packets: {self.already_asked_for_data}")
        if missing_pkt and not self.already_asked_for_data:
            print(f"ask for packet: {missing_pkt}")
            self.already_asked_for_data = True  # set flag to not repeat ask
            print(f"already asked for data: {self.already_asked_for_data}")
            self.root_app.after(5*60000, self.clear_ask_for_data_flag)  # wait 10 mins and clear the flag
            self.connection.ask_for_stored_data(device, missing_pkt)

    def clear_ask_for_data_flag(self):
        self.already_asked_for_data = False
        print(f"cleared asked for data: {self.already_asked_for_data}")

    def get_missing_packets_deprecated(self, device):
        print(f"updating packets with remote data: {device}")
        missing_ids = []
        device_data = self.positions[device]
        for i in range(1, device_data.latest_packet_id + 1):
            print(f"comparing {i} in {device_data.packet_ids} or {device_data.stored_packets}")
            if i not in device_data.packet_ids:
                if i not in device_data.stored_packets:
                    missing_ids.append(i)
        return missing_ids
        # self.check_prev_reads(device, self.devices[device].latest_packet_id)

    def check_prev_reads_dep(self, device, num_packets):
        print(f"Updating packets for {num_packets} packets")
        # print(f"{self.devices}")
        # print(f"for device: {device}")
        # print(f"we have packets: {self.devices[device].packet_ids}")

        for i in range(1, num_packets + 1):
            # print(f"Comparing {i} in {self.devices[device].packet_ids}")
            # print(f"{type(i)} {type(self.devices[device].packet_ids)} {type(self.devices[device].packet_ids[0])}")
            if i in self.positions[device].packet_ids:
                print(f"We already have packet: {i}")
            else:
                print(f"getting packet: {i}")

    def update_latest_packet_id(self, device, pkt_num):
        # this is the first method to see the device so add it to devices
        if device not in self.positions:
            self.add_device(device)
        self.positions[device].latest_packet_id = pkt_num

    # def add_mqtt_data(self, data_pkt):
    #     device = data_pkt["device"]

    def add_db_data(self, data_pkt):
        device = data_pkt["Info"]["device"]
        # if device is not seen yet, add it to device dict
        if device not in self.positions:
            self.add_device(device)
            # self.devices[device] = DeviceData()
            self.master_graph.add_device(device)

        time = datetime.datetime.strptime(data_pkt[TIME_KEYWORD], "%H:%M:%S").time()
        today = datetime.date.today()
        full_time = datetime.datetime.combine(today, time)
        print(time)
        print(type(data_pkt["Info"][CPUTEMP_KEYWORD]))
        self.positions[device].add_data_pt(full_time,
                                           float(data_pkt["Info"][CPUTEMP_KEYWORD]),
                                           float(data_pkt["Info"][ORYZONAL_KEYWORD]))

    @staticmethod
    def make_file(filepath, header):
        print(f"making file with header: {header}")
        try:
            with open(filepath, 'x') as _file:
                # use 'x' to try to make the file, if it exists
                # it will raise an error and just pass
                header.append('\n')
                _file.write(', '.join(header))
        except Exception as error:
            print(f"Error making file: {filepath}, error: {error}")

    def __str__(self):
        if not self.positions:
            _str = "No device"
        else:
            _str = ""
            for device in self.positions:
                _str += f"{device} properties:"
                _str += f"{self.positions[device]}\n"
        return _str


if __name__ == "__main__":
    dd = DeviceData()
    pkt = b'{"time": "07:03:39", "date": "2021-12-24", "packet_id": 42, "device": "position 1", "mode": "live", "OryConc": -1090446, "Raw_data": [249.93959045410156, 249.94522094726562, 249.9626007080078, 249.93377685546875, 249.99098205566406, 249.94097900390625, 250.0230255126953, 250.04856872558594, 250.0248260498047, 249.92759704589844, 250.0161895751953, 249.9507598876953, 250.06317138671875, 249.98680114746094, 249.95445251464844, 249.9587860107422, 249.99777221679688, 250.01380920410156, 249.93478393554688, 249.95440673828125, 249.9919891357422, 249.93399047851562, 249.9459991455078, 250.0257568359375, 249.94842529296875, 250.01756286621094, 250.0478057861328, 249.94923400878906, 249.94558715820312, 250.00140380859375, 249.95303344726562, 249.94984436035156, 249.99639892578125, 249.92559814453125, 249.9063720703125, 250.0, 249.97500610351562, 250.03997802734375, 250.0527801513672, 249.91041564941406, 250.0210418701172, 249.97119140625, 250.0321807861328, 249.88140869140625, 249.98898315429688, 249.9333953857422, 249.9546356201172, 249.9278564453125, 250.06280517578125, 250.08460998535156, 250.05203247070312, 249.9522247314453, 249.99339294433594, 249.9678192138672, 249.9716033935547, 249.98080444335938, 250.02439880371094, 249.88198852539062, 249.9532012939453, 249.92401123046875, 249.9735870361328, 249.93658447265625, 249.9412078857422, 249.93304443359375, 249.9438018798828, 250.0342254638672, 249.94818115234375, 249.9942169189453, 249.96441650390625, 249.91561889648438, 250.00616455078125, 249.99761962890625, 249.95437622070312, 250.017578125, 249.9233856201172, 249.97836303710938, 249.9818115234375, 250.0033721923828, 249.98660278320312, 250.0756072998047, 249.9437255859375, 249.9952392578125, 249.94061279296875, 249.83441162109375, 249.99839782714844, 250.0161895751953, 249.9766082763672, 249.95980834960938, 249.91636657714844, 249.89859008789062, 249.91238403320312, 250.01736450195312, 249.93960571289062, 250.0644073486328, 249.92478942871094, 250.04624938964844, 249.97540283203125, 249.9121856689453, 249.9148406982422, 249.94378662109375, 249.95777893066406, 250.0036163330078, 250.04058837890625, 249.98680114746094, 250.00355529785156, 249.9717559814453, 249.90696716308594, 250.0483856201172, 249.9302520751953, 249.9985809326172, 249.98019409179688, 249.9295654296875, 249.96820068359375, 249.9130096435547, 250.0527801513672, 250.0545654296875, 249.95677185058594, 249.97361755371094, 250.12921142578125, 249.89816284179688, 249.8993682861328, 249.9503936767578, 250.0, 250.00299072265625, 249.97335815429688, 249.8867950439453, 249.9827880859375, 249.92022705078125, 249.93423461914062, 250.10081481933594, 250.03720092773438, 249.9597625732422, 249.96661376953125, 250.05043029785156, 249.98439025878906, 250.0623779296875, 249.94717407226562, 250.00381469726562, 249.9661865234375, 250.0689697265625, 249.96002197265625, 249.9737548828125, 250.0966033935547, 249.90176391601562, 250.00099182128906, 249.97000122070312, 250.00933837890625, 249.9697723388672, 250.05079650878906, 250.06680297851562, 249.93179321289062, 249.9951934814453, 250.00099182128906, 249.96279907226562, 249.94664001464844, 249.96107482910156, 250.08717346191406, 250.0210418701172, 250.06736755371094, 249.9129638671875, 249.97738647460938, 249.98179626464844, 250.0697784423828, 249.91839599609375, 250.00619506835938, 249.96653747558594, 250.03758239746094, 250.07176208496094, 250.06558227539062, 250.0186004638672, 249.94619750976562, 249.9569854736328, 250.033203125, 250.0399932861328, 250.0989990234375, 250.02342224121094, 249.99258422851562, 249.9236297607422, 249.9506072998047, 249.96519470214844, 250.0074005126953, 250.05857849121094, 249.99896240234375, 250.01101684570312, 249.96421813964844, 250.01319885253906, 249.96240234375, 249.94244384765625, 250.08921813964844, 250.03018188476562, 250.07379150390625, 249.96514892578125, 250.02699279785156, 249.99241638183594, 249.96656799316406, 250.14939880371094, 249.9440460205078, 250.04441833496094, 250.1304168701172, 250.05836486816406, 249.90658569335938, 250.0889892578125, 250.0143585205078, 250.08901977539062, 250.0081787109375, 250.0664520263672, 250.0284423828125, 249.96505737304688, 250.06663513183594, 249.98818969726562, 249.98382568359375, 250.0076141357422, 250.0491943359375, 250.04037475585938, 250.0605926513672, 250.07337951660156, 250.13973999023438, 250.05519104003906, 249.92982482910156, 250.0472412109375, 250.06298828125, 250.0136260986328, 250.09121704101562, 250.0036163330078, 250.05101013183594, 249.98162841796875, 250.05816650390625, 249.9145965576172, 249.97305297851562, 249.9891815185547, 250.08621215820312, 250.05120849609375, 250.08920288085938, 249.98660278320312, 250.02357482910156, 250.0264129638672, 250.07940673828125, 250.08580017089844, 250.01779174804688, 250.1352081298828, 250.07106018066406, 250.08322143554688, 250.0992431640625, 249.96498107910156, 250.05824279785156, 250.10079956054688, 250.13241577148438, 249.97300720214844, 250.03257751464844, 250.01959228515625, 249.9469757080078, 249.8757781982422, 250.04385375976562, 250.04415893554688, 249.98858642578125, 250.0198211669922, 250.0054473876953, 250.02023315429688, 250.09121704101562, 250.10060119628906, 250.0110321044922, 250.04238891601562, 250.0895538330078, 250.08265686035156, 250.2152099609375, 250.04957580566406, 250.00621032714844, 250.07757568359375, 249.98760986328125, 249.89918518066406, 250.01739501953125, 250.1471710205078, 250.10316467285156, 250.05641174316406, 249.9365997314453, 250.01483154296875, 250.1199951171875, 250.03123474121094, 250.0023651123047, 250.0600128173828, 250.09207153320312, 250.03025817871094, 250.05043029785156, 249.97640991210938, 249.99203491210938, 249.95103454589844, 250.04640197753906, 250.05218505859375, 250.0370330810547, 250.0684051513672, 249.90380859375, 250.009765625, 250.1058349609375, 250.0894317626953, 249.9892120361328, 250.10960388183594, 249.9642333984375, 250.08682250976562, 249.97677612304688, 250.12075805664062, 250.01199340820312], "CPUTemp": "48.85", "SensorTemp": "32.98"}'
    pkt2 = b'{"time": "07:05:39", "date": "2021-12-24", "packet_id": 45, "device": "position 1", "mode": "live", "OryConc": -1090446, "Raw_data": [249.93959045410156, 249.94522094726562, 249.9626007080078, 249.93377685546875, 249.99098205566406, 249.94097900390625, 250.0230255126953, 250.04856872558594, 250.0248260498047, 249.92759704589844, 250.0161895751953, 249.9507598876953, 250.06317138671875, 249.98680114746094, 249.95445251464844, 249.9587860107422, 249.99777221679688, 250.01380920410156, 249.93478393554688, 249.95440673828125, 249.9919891357422, 249.93399047851562, 249.9459991455078, 250.0257568359375, 249.94842529296875, 250.01756286621094, 250.0478057861328, 249.94923400878906, 249.94558715820312, 250.00140380859375, 249.95303344726562, 249.94984436035156, 249.99639892578125, 249.92559814453125, 249.9063720703125, 250.0, 249.97500610351562, 250.03997802734375, 250.0527801513672, 249.91041564941406, 250.0210418701172, 249.97119140625, 250.0321807861328, 249.88140869140625, 249.98898315429688, 249.9333953857422, 249.9546356201172, 249.9278564453125, 250.06280517578125, 250.08460998535156, 250.05203247070312, 249.9522247314453, 249.99339294433594, 249.9678192138672, 249.9716033935547, 249.98080444335938, 250.02439880371094, 249.88198852539062, 249.9532012939453, 249.92401123046875, 249.9735870361328, 249.93658447265625, 249.9412078857422, 249.93304443359375, 249.9438018798828, 250.0342254638672, 249.94818115234375, 249.9942169189453, 249.96441650390625, 249.91561889648438, 250.00616455078125, 249.99761962890625, 249.95437622070312, 250.017578125, 249.9233856201172, 249.97836303710938, 249.9818115234375, 250.0033721923828, 249.98660278320312, 250.0756072998047, 249.9437255859375, 249.9952392578125, 249.94061279296875, 249.83441162109375, 249.99839782714844, 250.0161895751953, 249.9766082763672, 249.95980834960938, 249.91636657714844, 249.89859008789062, 249.91238403320312, 250.01736450195312, 249.93960571289062, 250.0644073486328, 249.92478942871094, 250.04624938964844, 249.97540283203125, 249.9121856689453, 249.9148406982422, 249.94378662109375, 249.95777893066406, 250.0036163330078, 250.04058837890625, 249.98680114746094, 250.00355529785156, 249.9717559814453, 249.90696716308594, 250.0483856201172, 249.9302520751953, 249.9985809326172, 249.98019409179688, 249.9295654296875, 249.96820068359375, 249.9130096435547, 250.0527801513672, 250.0545654296875, 249.95677185058594, 249.97361755371094, 250.12921142578125, 249.89816284179688, 249.8993682861328, 249.9503936767578, 250.0, 250.00299072265625, 249.97335815429688, 249.8867950439453, 249.9827880859375, 249.92022705078125, 249.93423461914062, 250.10081481933594, 250.03720092773438, 249.9597625732422, 249.96661376953125, 250.05043029785156, 249.98439025878906, 250.0623779296875, 249.94717407226562, 250.00381469726562, 249.9661865234375, 250.0689697265625, 249.96002197265625, 249.9737548828125, 250.0966033935547, 249.90176391601562, 250.00099182128906, 249.97000122070312, 250.00933837890625, 249.9697723388672, 250.05079650878906, 250.06680297851562, 249.93179321289062, 249.9951934814453, 250.00099182128906, 249.96279907226562, 249.94664001464844, 249.96107482910156, 250.08717346191406, 250.0210418701172, 250.06736755371094, 249.9129638671875, 249.97738647460938, 249.98179626464844, 250.0697784423828, 249.91839599609375, 250.00619506835938, 249.96653747558594, 250.03758239746094, 250.07176208496094, 250.06558227539062, 250.0186004638672, 249.94619750976562, 249.9569854736328, 250.033203125, 250.0399932861328, 250.0989990234375, 250.02342224121094, 249.99258422851562, 249.9236297607422, 249.9506072998047, 249.96519470214844, 250.0074005126953, 250.05857849121094, 249.99896240234375, 250.01101684570312, 249.96421813964844, 250.01319885253906, 249.96240234375, 249.94244384765625, 250.08921813964844, 250.03018188476562, 250.07379150390625, 249.96514892578125, 250.02699279785156, 249.99241638183594, 249.96656799316406, 250.14939880371094, 249.9440460205078, 250.04441833496094, 250.1304168701172, 250.05836486816406, 249.90658569335938, 250.0889892578125, 250.0143585205078, 250.08901977539062, 250.0081787109375, 250.0664520263672, 250.0284423828125, 249.96505737304688, 250.06663513183594, 249.98818969726562, 249.98382568359375, 250.0076141357422, 250.0491943359375, 250.04037475585938, 250.0605926513672, 250.07337951660156, 250.13973999023438, 250.05519104003906, 249.92982482910156, 250.0472412109375, 250.06298828125, 250.0136260986328, 250.09121704101562, 250.0036163330078, 250.05101013183594, 249.98162841796875, 250.05816650390625, 249.9145965576172, 249.97305297851562, 249.9891815185547, 250.08621215820312, 250.05120849609375, 250.08920288085938, 249.98660278320312, 250.02357482910156, 250.0264129638672, 250.07940673828125, 250.08580017089844, 250.01779174804688, 250.1352081298828, 250.07106018066406, 250.08322143554688, 250.0992431640625, 249.96498107910156, 250.05824279785156, 250.10079956054688, 250.13241577148438, 249.97300720214844, 250.03257751464844, 250.01959228515625, 249.9469757080078, 249.8757781982422, 250.04385375976562, 250.04415893554688, 249.98858642578125, 250.0198211669922, 250.0054473876953, 250.02023315429688, 250.09121704101562, 250.10060119628906, 250.0110321044922, 250.04238891601562, 250.0895538330078, 250.08265686035156, 250.2152099609375, 250.04957580566406, 250.00621032714844, 250.07757568359375, 249.98760986328125, 249.89918518066406, 250.01739501953125, 250.1471710205078, 250.10316467285156, 250.05641174316406, 249.9365997314453, 250.01483154296875, 250.1199951171875, 250.03123474121094, 250.0023651123047, 250.0600128173828, 250.09207153320312, 250.03025817871094, 250.05043029785156, 249.97640991210938, 249.99203491210938, 249.95103454589844, 250.04640197753906, 250.05218505859375, 250.0370330810547, 250.0684051513672, 249.90380859375, 250.009765625, 250.1058349609375, 250.0894317626953, 249.9892120361328, 250.10960388183594, 249.9642333984375, 250.08682250976562, 249.97677612304688, 250.12075805664062, 250.01199340820312], "CPUTemp": "48.85", "SensorTemp": "32.98"}'

    data_pkt = json.loads(pkt)
    print(data_pkt)
    devices = DEVICES[:]
    devices.append("AV")
    models = model.Models(devices)

    dd.add_data_pkt(data_pkt, models)
    dd.add_data_pkt(json.loads(pkt2), models)
