# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Classes to hold the data for NIR sensors measuring
oryzanol concentrations on an IoT sensor.
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import csv
import datetime as dt
import json
import logging
import os
import shutil
import tkinter as tk  # type hinting
from typing import List

# installed libraries
from codetiming import Timer
from numpy import array, nan, searchsorted
from psutil import cpu_count, getloadavg, virtual_memory
from psutil._common import bytes2human

# sys.path.append(os.getcwd())
# sys.path.append('/Users/kylesmac/PycharmProjects/NIR_ROB/GUI')
# print(sys.path)
# local files
import global_params
import helper_functions
import model

# Test and run log files are different, but messages are the same
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

MAX_DATA_PTS = 600
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
# FACTORY_DIR = "C:\Users\nirsb\OneDrive - Surin Bran Oil Co.,Ltd\Documents\Refine Process NIR\Data"
FACTORY_DIR = os.path.join("C:", os.sep, "Users", "nirsb", "OneDrive - Surin Bran Oil Co.,Ltd",
                           "Documents", "Refine Process NIR", "Data")
TIME_KEYWORD = "Datetime"
CPUTEMP_KEYWORD = "CPUTemp"
ORYZONAL_KEYWORD = "OryConc"
with open(os.path.join(__location__, "sensor_settings.json")) as _file:
    json_data = _file.read()
SENSOR_INFO = json.loads(json_data)
DEVICES = list(global_params.DEVICES.keys())
POSITIONS = list(global_params.POSITIONS.keys())
with open(os.path.join(__location__, "new_models.json")) as _file:
    json_data = _file.read()
MODEL_INFO = json.loads(json_data)
USE_LOCAL_MODEL = True
#
#
with open(os.path.join(__location__, "master_settings.json")) as _file:
    json_data2 = _file.read()
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
CPU_COUNT = cpu_count()

indices = dict()
for header in FILE_HEADER:
    indices[header] = FILE_HEADER.index(header)


def log_cpu_ram_usage():
    """ Write into the logger the cpu and RAM usage """
    print(getloadavg(), cpu_count())
    cpu_loads = [x / CPU_COUNT for x in getloadavg()]
    virt_mem = virtual_memory()
    ram_usage = bytes2human(virt_mem.used)
    logger.info(f"cpu loads: {cpu_loads}")
    logger.info(f"ram percentage: {virt_mem.percent}, ram used: {ram_usage}")


def isfloat(str_to_test: str) -> bool:
    """
    Test if the argument passed in can be converted to an int

    Args:
        str_to_test (str): string to test

    Returns:
        True if the argument can be converted to int, else False

    Test
    --------------
    >>> isfloat("1")
    True
    >>> isfloat("b")
    False
    >>> isfloat("1.543")
    True
    """
    try:
        float(str_to_test)
        return True
    except ValueError:
        return False


def isint(str_to_test: str) -> bool:
    """
    Test if the argument passed in can be converted to an int

    Args:
        str_to_test (str): string to test

    Returns:
        True if the argument can be converted to int, else False

    Test
    --------------
    >>> isint("1")
    True
    >>> isint("b")
    False
    >>> isint("1.543")
    False
    """
    try:
        int(str_to_test)
        return True
    except ValueError:
        return False


def log_deprecation_violation(msg):
    with open("deprecation_logger.txt", 'w', encoding='utf-8') as log_file:
        log_file.write(msg)


def extract_time_stamp(_date_str: str) -> str:
    """
    Test if the input string has a valid time format, either "%H:%M:%S", or
    "%Y-%m-%d %H:%M:%S" and return just the time stamp, or an empty string if
    it is not in either format

    Args:
        _date_str (str): string to test for a valid date

    Returns:
        str: string with the time if there was a valid date time string
        passed in; else an empty string if it was not a valid time

   Test
    -------------
    >>> extract_time_stamp("bbb")
    ''
    >>> extract_time_stamp("2023-05-12 10:25:45")
    '10:25:45'
    >>> extract_time_stamp("13:45:30")
    '13:45:30'
    >>> extract_time_stamp("2023-05-12")
    ''
    >>> extract_time_stamp(' 00:02:37')
    '00:02:37'
   """
    formats = ["%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
    time_stamp = ""

    for fmt in formats:
        try:
            datetime_obj = dt.datetime.strptime(_date_str.strip(), fmt)
            time_stamp = datetime_obj.strftime("%H:%M:%S")
            break
        except ValueError:
            continue
    return time_stamp


# TODO: convert DataPacket class to set of functions
def convert_csv_row_to_packet(csv_row_list: List[str]) -> dict:
    """
    Convert a list from the csv save file into a dictionary, similar
    to the data packet received from the sensor.  If the list of
    csv entries is not formatted correctly, this will return an empty dict

    Args:
        csv_row_list (list): the row from the saved csv file, already split
        into a list on the commas

    Returns:
        dict: data packet format with each column of the csv file put
        with the proper key

    Test
    -------------
    >>> convert_csv_row_to_packet(['', '', '', '', '', '', '', ''])
    {}
    >>> convert_csv_row_to_packet(['2023-03-07 00:02:53', 'position 1', '15746.0',
    '29.0', '40.2', '0.0', '0'])
    {'packet_id': 0, 'position': 'position 1', 'time': '00:02:53', 'CPUTemp': 40.2,
    'SensorTemp': 0.0, 'OryConc': 15746.0, 'AV': 29.0}
    """
    # incase there was any white space in the file, strip all white space first

    pkt = {}
    if isint(csv_row_list[indices["packet_id"]]):
        # use local function to test if packet id can be converted
        pkt["packet_id"] = int(csv_row_list[indices["packet_id"]])
    else:  # ignore packet id that is missing or formatted wrong
        return {}
    pkt["position"] = csv_row_list[indices["position"]].strip()
    if pkt["position"] not in POSITIONS:
        # log message to test this works, try to catch if the device was sent instead
        logger.error(f"received message from device not in POSITIONS list| pkt: {pkt}")
        return {}  # ignore messages from devices not in list

    # for time strip the date from it, split at the space between
    # the data and time and take the time at the end
    pkt["time"] = extract_time_stamp(csv_row_list[indices["time"]])

    for obj in ["CPUTemp", "SensorTemp", "OryConc"]:
        if isfloat(csv_row_list[indices[obj]]):
            pkt[obj] = float(csv_row_list[indices[obj]])
    try:  # this will be a ' ' if there is no AV key
        pkt['AV'] = float(csv_row_list[indices['AV']])
    except:
        pass
        # pkt['AV'] = None
    return pkt


class DataPacket:
    def __init__(self, date=None, time=None, packet_id=None,
                 device=None, raw_data=None, ory_conc=None,
                 av_value=None, cpu_temp=None,
                 sensor_temp=None, mode=None, packet=None,
                 data_line=None):
        log_deprecation_violation("DataPacket called")
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
        elif packet_id is not None:  # can be 0 and legit
            self.time = time
            self.device = device
            self.packet_id = packet_id
            # the rest are assigned above
            self.make_packet()
        elif data_line:
            self.parse_line(data_line)
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
        # this packet is send through json so truncate the raw data floats
        # TODO: is this worth it?

    def parse_line(self, csv_line):
        split_line = csv_line.split(",")
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
    def __init__(self, use_av=False):
        self.time_series = []
        self.packet_ids = []
        self.cpu_temp = []
        self.sensor_temp = []
        self.oryzanol = []
        self.ory_rolling = []
        self.use_av = use_av
        self.av = []
        self.av_rolling = []

        self.today = dt.datetime.today().date()
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
            if len(self.av) > 0:
                row = [self.time_series[i].strftime("%Y-%m-%d %H:%M:%S"),
                       position, self.oryzanol[i],
                       self.av[i], self.cpu_temp[i],
                       self.sensor_temp[i], self.packet_ids[i]]
            else:
                row = [self.time_series[i].strftime("%Y-%m-%d %H:%M:%S"),
                       position, self.oryzanol[i],
                       '', self.cpu_temp[i],
                       self.sensor_temp[i], self.packet_ids[i]]
            print(f"row: {row}")
            csv_writer.writerow(row)

    def update_date(self, date):
        self.today = dt.datetime.today().date()
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
        # print(f"add data pkt: {data_pkt}")
        # print(f"cwd data_class: {os.getcwd()}")
        insert_idx = self.check_pkt_id_get_insert_idx(data_pkt)
        # print(f"insert index: {insert_idx}")
        if insert_idx is None:
            return None  # no pkt id, or one already received
        # print(f"sort idx: {insert_idx}, len packet id: {len(self.packet_ids)}")
        if "AV" in data_pkt :
            # print(f"inserting AV: {data_pkt['AV']}")
            self.av.insert(insert_idx, float(data_pkt["AV"]))

            # print(f"adding av: {insert_idx}, {float(data_pkt['AV'])}, {self.av}")
        elif self.use_av:
            self.av.insert(insert_idx, nan)

        if "device" in data_pkt:  # this is the code in the sensors still
            position = data_pkt["device"].strip()
        elif "position" in data_pkt:  # trying to move all code to here
            position = data_pkt["position"]
        else:
            raise KeyError("data packet has to have 'position' or 'device' in it")

        device = global_params.POSITIONS[position]
        # print(f"device: {device}")
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
            self.cpu_temp.insert(insert_idx, nan)
        if "SensorTemp" in data_pkt:
            sensor_temp = float(data_pkt["SensorTemp"])
            self.sensor_temp.insert(insert_idx, sensor_temp)
        else:
            self.sensor_temp.insert(insert_idx, nan)

        self.packet_ids.insert(insert_idx, int(data_pkt["packet_id"]))
        print(f"packet time: {data_pkt['time']}")
        print(f"packet: {data_pkt}")
        if len(data_pkt["time"]) <= 8:
            time = dt.datetime.strptime(data_pkt["time"], "%H:%M:%S").time()
            time = dt.datetime.combine(self.today, time)
        else:
            time = data_pkt["time"]
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
            # print(f"got packet_id--: {_pkt_id}")
        else:
            # print(f"No packet id, abondoning data")
            return None
        _sort_idx = searchsorted(array(self.packet_ids), _pkt_id)
        #         print(f"{_pkt_id in self.packet_ids}, pkt ids: {self.packet_ids}")
        if _pkt_id in self.packet_ids:
            # print(f"Already received pkt id: {_pkt_id}")
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
        # print("Init Time Stream Data")
        # print(f"FILE HEADER: {FILE_HEADER}")
        logging.debug(f"dt2: {dt.datetime.now()}")
        self.master_graph = root_app.graphs
        self.connection = None
        devices = DEVICES[:]  # copy to append to it
        devices.append("AV")
        self.models = model.Models(devices)
        # this is not pretty
        # TODO: remove dependance inject, this uses after and the info frame
        # Move afters to main, and import info frame directly
        self.root_app = root_app  # type: tk.Tk
        self.update_after = None
        self.positions = {}
        # this is needed to make the datetime in the data
        self.today = dt.datetime.today().strftime("%Y-%m-%d")
        logging.debug(f"dt device data: {self.today}")
        # message_id to prevent repeately asking for the same data
        self.already_asked_for_data = False
        # make these in make_save_files() has to make these on new days also
        self.save_file = None
        self.save_raw_data_file = None
        if not self.check_previous_data():
            print("No previous data so making file")
            self.make_save_files()

    def check_previous_data(self):
        today = dt.datetime.today().strftime("%Y-%m-%d")
        data_path = os.path.join(__location__, "data")
        self.save_file = os.path.join(data_path, f"{today}.csv")
        if os.path.isfile(self.save_file):
            # file exists so load it
            print("loading previous data")
            self.load_previous_data()
            # save the data after sorting
            print(self.positions)
            # print('device data 2:', self.positions["position 2"].oryzanol)
            self.save_summary_data()
            return True
        return False

    def make_save_files(self):
        # check if there is already a file with today's data
        today = dt.datetime.today().strftime("%Y-%m-%d")
        data_path = os.path.join(__location__, "data")
        self.save_file = os.path.join(data_path, f"{today}.csv")
        self.save_raw_data_file = os.path.join(data_path, f"{today}_raw_data.csv")
        try:  # the factory computer wants a different directory
            if os.path.isdir(FACTORY_DIR):
                self.save_file = os.path.join(FACTORY_DIR, f"{today}.csv")
                print(f"Saving to factory dir: {self.save_file}")
        except Exception as e:
            print("no factory directory")
        self.make_file(self.save_file, FILE_HEADER)
        if LOG_RAW_DATA and not os.path.isfile(self.save_raw_data_file):
            self.make_file(self.save_raw_data_file, RAW_DATA_HEADERS)

    def load_previous_data(self):
        print(f"load file: {self.save_file}")
        with open(self.save_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                # print(f"line count: {line_count}, len row: {len(row)}")
                if line_count != 0 and len(row) >= 7:
                    print(f"load row: {row}")
                    self.add_csv_data(row)
                line_count += 1

    def save_summary_data(self):
        # print(f"saving data: {self.positions}")
        with open('sorted_file.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            # write header
            writer.writerow(FILE_HEADER)
            for position in self.positions:
                # print(f"saving positions: {position}")
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
            if position == "position 1" or position == "position 2":
                self.positions[position] = DeviceData(use_av=True)
            else:
                self.positions[position] = DeviceData()
        else:
            print(f"{position} is not on the list, part 2")

    def add_csv_data(self, csv_row):
        """ Add data from a csv row, this will be saved data """
        # position = csv_row[indices["position"]].strip()
        data_pkt = convert_csv_row_to_packet(csv_row)
        print(f"adding data_pkt: {data_pkt}")
        if "position" not in data_pkt:
            return  # ignore not proper data_pkt
        position = data_pkt["position"]
        # print(f"adding csv data for position: {position}")
        if position:
            if position in POSITIONS and position not in self.positions:
                self.add_device(position)
            device_data = self.positions[position]
            device_data.add_data_pkt(data_pkt, self.models)
            print(f"len: {len(device_data.time_series)}")

    @Timer(name="add_data", text="Time: {:.4f}", logger=logging.debug)
    def add_data(self, data_pkt: dict, save_data_pkt=True):
        # TODO: fix this, its a mess
        # print(f"data_pkt: {data_pkt}")
        # print(f"dt3: {dt.datetime.now()}")
        logger.info(f"adding data packet: {data_pkt}")
        if type(data_pkt) is not dict:
            return 204  # TODO: sometimes an int gets in here.  look at sensor code to fix
        # if data is from a database, it has to be converted first
        data_pkt = helper_functions.check_database_info(data_pkt)
        if "device" in data_pkt:
            position = data_pkt["device"].strip()
        elif "position" in data_pkt:
            position = data_pkt["position"].strip()
        else:
            print("No 'device' or 'position' in data_pkt")
            return 200
        if position not in self.positions:
            print(f"adding device2: {position}")
            self.add_device(position)

        device_data = self.positions[position]  # type: DeviceData

        # check if date has changed
        packet_date = data_pkt["date"]
        packet_datetime = dt.datetime.strptime(packet_date, "%Y-%m-%d").date()
        current_date = device_data.today
        # print(f"dt4: {current_date}")
        if packet_date != str(current_date):
            print(f"This is a different day. Today {current_date}, packet date {packet_date}")
            # test if date advanced at midnight and files need to update
            if packet_datetime == device_data.today + dt.timedelta(days=1):
                # TODO: check the date is really changed
                self.update_date(None)  # make the new file
                device_data.update_date(None)  # tell device_data to update
            # elif packet_datetime == device_data.today - timedelta(days=1):
            else:
                # old data was received, just ignore it rather than figure out if its needed
                # print(f"packet data: {packet_date}, current date: {current_date}")
                return 201  # testing unit code
        # add the date to the individual sensor data class
        data_pkt = device_data.add_data_pkt(data_pkt, self.models)
        # device_data.resize_data()
        if not data_pkt:
            return 222
        # print(f"ask 2: {self.already_asked_for_data}")
        # print(f"ask 2b: {device_data.ask_for_missing_packets}")
        if data_pkt and device_data.ask_for_missing_packets and \
                not self.already_asked_for_data:  # this is not data loaded from file
            # or the sensor is not currently sending saved data
            self.already_asked_for_data = True
            self.root_app.after(5*60000, self.clear_ask_for_data_flag)
            missing_pkt = self.find_next_missing_pkts(device_data, int(data_pkt["packet_id"]))
            logging.debug(f"ask for packets: {missing_pkt} from position: {position}")
            if self.connection:  # for testing or offline
                self.connection.ask_for_stored_data(position, missing_pkt)
                device_data.ask_for_missing_packets = False

        if "Raw_data" in data_pkt and save_data_pkt:
            self.master_graph.update_spectrum(data_pkt["Raw_data"], position)
        if not self.update_after:
            self.update_after = self.root_app.after(500, lambda: self.update_graph(position))

        if save_data_pkt:  # this is live data
            # TODO: update the ory conc value in this
            # print(f"saving data: {data_pkt['packet_id']}")
            self.save_data(data_pkt)
            self.root_app.info.check_in(position)
            # only update the info frame if the is newer data than
            # the data saved
            self.root_app.info.update_current_info(data_pkt, position)
        if logger.isEnabledFor(logging.INFO):  # only get statitics if log is set high enough
            log_cpu_ram_usage()
        return 0

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
        print(f"Updating graph for position: {position}")
        device_data = self.positions[position]  # type: DeviceData
        self.master_graph.update_notebook(position, device_data)
        self.update_after = None

    def find_next_missing_pkts(self, device_data, last_pkt_id):
        missing_pkts = []
        for i in range(last_pkt_id):
            if i not in device_data.packet_ids:
                missing_pkts.append(i)
        return missing_pkts

    def save_data(self, data_pkt):
        # make a string of the data and write it
        data_list = []

        date = dt.datetime.strptime(data_pkt["date"], "%Y-%m-%d")
        time = dt.datetime.strptime(data_pkt["time"], "%H:%M:%S").time()

        data_pkt["time"] = dt.datetime.combine(date, time)
        for item in FILE_HEADER_TO_SAVE:
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
            with open(self.save_file, 'a', encoding="utf8") as _file:
                _file.write(', '.join(data_list))
        except Exception as _error:
            # do something here to save the list and write later
            print(f"Error in saving data: {_error}")
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
                with open(self.save_raw_data_file, 'a', encoding="utf8") as _file:
                    _file.write(', '.join(data_list2))
                    if "\n" not in data_list2[-1]:
                        _file.write("\n")

    def clear_ask_for_data_flag(self):
        self.already_asked_for_data = False
        print(f"cleared asked for data: {self.already_asked_for_data}")

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

        time = dt.datetime.strptime(data_pkt[TIME_KEYWORD], "%H:%M:%S").time()
        today = dt.date.today()
        full_time = dt.datetime.combine(today, time)
        self.positions[device].add_data_pt(full_time,
                                           float(data_pkt["Info"][CPUTEMP_KEYWORD]),
                                           float(data_pkt["Info"][ORYZONAL_KEYWORD]))

    @staticmethod
    def make_file(filepath, header):
        """
        NOTE: DO NOT CHANGE header, SOME CONSTANTS GET PASSED IN THERE
        Args:
            filepath:
            header list[str]: DO NOT CHANGE.

        Returns:

        """
        try:
            with open(filepath, 'x', encoding="utf8") as _file:
                # use 'x' to try to make the file, if it exists
                # it will raise an error and just pass
                _file.write(', '.join(header))
                _file.write('\n')
        except FileExistsError as error:
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
    log_deprecation_violation("test")
