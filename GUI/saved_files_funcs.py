# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import csv
from datetime import datetime
import os

# installed libraries
import numpy as np

# local files
import data_class
import global_params

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

N_SUMMARY_COLUMNS = len(data_class.FILE_HEADER)
N_RAW_COLUMNS = len(data_class.RAW_DATA_HEADERS)
POSITIONS = global_params.POSITIONS.keys()


def sort_file(filename, n_columns=0):
    filename = os.path.join(__location__, filename)
    print(filename)
    try:
        data = np.genfromtxt(filename, names=True,
                             dtype=None, delimiter=',',
                             encoding='bytes',
                             autostrip=True,
                             usecols=np.arange(0, n_columns))
    except Exception as _error:
        line_number = str(_error).split('#')[1].split(' ')[0]
        fix_file(filename, line_number, n_columns)
        data = np.genfromtxt(filename, names=True,
                             dtype=None, delimiter=',',
                             encoding='bytes',
                             autostrip=True,
                             usecols=np.arange(0, n_columns))
    # remove any duplicate data if is in file
    data = np.unique(data)
    header_str = str(data.dtype.names[:7]).replace("'", "")
    header_str = header_str.replace('(', "").replace(')', "")
    sorted_str = header_str + ",\n"
    for device_position in POSITIONS:
        sorted_str += get_position_data(data, device_position)
        sorted_str += "\n"
    # sorted_str = sort_position_data(data)
    with open(os.path.join(__location__, filename), "w") as _file:
        # _file.write(str(data.dtype.names))
        _file.write(sorted_str)


def fix_file(filename, line_num, n_cols):
    print(filename)
    backup_file = filename + ".bak"
    csv_reader = csv.reader(open(filename, 'r'))
    file_lines = []
    i = 0
    line_num = int(line_num)
    try:
        for line in csv_reader:
            if len(line) >= 7:
                print(f"a: {line}")
                file_lines.append(line)
    except:
        pass
    csv_writer = csv.writer(open(backup_file, 'w'))
    for wline in file_lines:
        # print(wline)
        csv_writer.writerow(wline)
    os.replace(backup_file, filename)


def get_position_data(_full_data, position):
    position = position.encode('utf-8')
    print(f"get position data: {position}")
    # print(_full_data)
    # print(np.unique(_full_data["device_number"]))
    # print(position in np.unique(_full_data["device_number"]))
    pos_data = _full_data[_full_data["device_number"] == position]

    # print(pos_data)
    return sort_position_data(pos_data)


def sort_position_data(_data):
    index1 = np.argsort(_data["packet_id"])
    data_sort = _data[index1]
    sorted_str = np.array2string(data_sort, separator=',')
    sorted_str = sorted_str.replace('(', '').replace(")", "")
    sorted_str = sorted_str.replace('[', '').replace("]", "")
    sorted_str = sorted_str.replace("False", "")
    sorted_str = sorted_str.replace("b'", "").replace("'", "")
    return sorted_str


def sort_files(date):
    summary_file = f"data/{date}.csv"
    raw_file = f"data/{date}_raw_data.csv"
    # sort summary file and raw data
    sort_file(summary_file, n_columns=N_SUMMARY_COLUMNS)
    sort_file(raw_file, n_columns=N_RAW_COLUMNS)


def load_saved_file(filename, data_struct: data_class.TimeStreamData):
    # This is the first data to be added to the data class
    # sort the data first
    sort_file(filename, n_columns=N_SUMMARY_COLUMNS)
    # then open it
    data = np.genfromtxt(filename, names=True,
                         dtype=None, delimiter=',',
                         encoding='bytes',
                         autostrip=True,
                         usecols=np.arange(0, N_SUMMARY_COLUMNS))
    # now fill in the fields for the data_class
    # print(data)
    for position in POSITIONS:
        load_position_data(data, position, data_struct)


def load_position_data(_data: data_class.TimeStreamData,
                       _pos: str, _data_struct: data_class.DeviceData):
    pos_data = _data[_data["device_number"] == _pos.encode('utf-8')]
    # print("pos data: ")
    # print(pos_data)
    if pos_data.shape[0] == 0:
        return  # no saved data for the position

    _data_struct.add_device(_pos)
    device_data = _data_struct.positions[_pos]
    today = datetime.today()
    pre_time_series = [t.decode("utf-8") for t in pos_data["time"]]
    pre2_time_series = [datetime.strptime(t, "%H:%M:%S").time() for t in pre_time_series]
    time_series = [datetime.combine(today, t) for t in pre2_time_series]
    device_data.time_series = time_series
    device_data.packet_ids = pos_data["packet_id"].tolist()
    device_data.cpu_temp = pos_data["CPUTemp"].tolist()
    device_data.sensor_temp = pos_data["SensorTemp"].tolist()
    device_data.oryzanol = pos_data["OryConc"].tolist()
    # print('popoy: ', device_data.time_series)
    # print(type(device_data.time_series))
    # print(device_data.sensor_temp)
    # print(device_data.cpu_temp)
    device_data.last_packet_id = device_data.packet_ids[-1]
    if "position 1" in _pos:
        device_data.av = pos_data["AV"].tolist()
        print(type(device_data.av))
        print(device_data.av)


if __name__ == "__main__":
    # file_name = "data/2021-12-14.csv"
    # sort_file(file_name)
    sort_files("2021-12-22")
