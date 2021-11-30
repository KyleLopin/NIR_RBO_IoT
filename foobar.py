# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import datetime
import json

import pandas as pd

# print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# print(datetime.datetime.now().time().strftime('%H:%M:%S'))
# print(datetime.date.today())
# filename = "Crude RBO.xlsx"
# data_coeff = pd.read_excel(filename,
#                            sheet_name="coeffs", index_col=0, engine='openpyxl')
# data_waves = pd.read_excel(filename,
#                            sheet_name="ref", index_col=0, engine='openpyxl')
#
# # print(data_coeff)
# pls_constant = data_coeff.loc["Constant"].tolist()
# print(f"pls constant = {pls_constant}")
#
# pls_coeff = data_coeff.iloc[1:].to_numpy().tolist()
# print("=====")
# print(pls_coeff)
# print(len(pls_coeff))
# #
# ref_intensity = data_waves["Intensity"].tolist()
# dark_intensity = data_waves["Dark intensity"].tolist()
# print(ref_intensity)
#
# json_model = {"Constant": pls_constant,
#               "Coeffs": pls_coeff,
#               "Ref Intensities": ref_intensity,
#               "Dark Intensities": dark_intensity}
# json_model = {"Constant": pls_constant,
#               "Coeffs": pls_coeff,
#               "Ref Intensities": ref_intensity}
# print(json_model)
# with open("sensor_settings.json", "r") as _file:
#     data = json.load(_file)
# print(data.keys())
# for device in data.keys():
#     print(device)
#     data[device]["pt scans"] = 100
#     data[device]["scan avgs"] = 60
#     for key in data[device].keys():
#         print(device, key)
#         print(data[device][key])
# with open("sensor_settings.json", "w") as _file:
#     json.dump(data, _file)
# LOAD JSON ===============
json_data = open("sensor_settings.json").read()
print(json_data)

json_model = json.loads(json_data)
print(json_model.keys())
for position in json_model.keys():
    print(json_model[position].keys())
# new_model = {}
# for device in ["position 1", "position 2", "position 3"]:
#     new_model[device] = json_model
#
# with open("sensor_settings.json", "r") as _file:
#     json.dump(json_model, _file)
#
# print(new_model)
# with open("sensor_settings.json", "w") as _file:
#     json.dump(new_model, _file)
# constant = json_model["Constant"]
# coeffs = json_model["Coeffs"]
# ref_waves = json_model["Ref Intensities"]
# dark_waves = json_model["Dark Intensities"]
# print(json_model.keys())
# =====================
# import numpy as np
# a = np.array([[1], [2], [3]])
# print(a.shape)
# print(a)
# print(a.reshape(1, -1))
# print(a.T)
# import socket
# import subprocess
# arpa = subprocess.check_output(("arp", "-a")).decode("ascii")
# print(arpa)
# print('-----')
# # arpa = subprocess.check_output(("arp", "-a"))
# # print(arpa)
#
# for line in arpa.split("\n"):
#     print('--')
#     print(line)
#     print('++')
#     if line:
#         ip = line.split("(")[1].split(")")[0]
#         print(ip)
#         # host = socket.gethostbyname(ip)
#         try:
#             # host = socket.gethostbyaddr(str(ip))
#
#             # print(host)
#             print("9999")
#             arpa = subprocess.check_output(["ping", "-c1", ip]).decode("ascii")
#             print(arpa)
#         except Exception as e:
#             print(f"Error: {e}")
# ham
#
# print('===')
# arpa = subprocess.check_output(["ping", "-c1", "raspberrypi.local"]).decode("ascii")
# print(arpa)
# ip_line = arpa.split("\n")[0]
# print("ip line:")
# print(ip_line)
# ip = ip_line.split("(")[1].split(")")[0]
# print(f"ip: {ip}")
# import numpy as np
# a = [1, 2]
# b = [1, 2, 3, 4, 5]
# print(a[-5:])
# print(b[-5:])
# print(np.array(a[-5:]).mean())
# print(np.array(b[-5:]).mean())
# RAW_DATA_HEADERS = ["time", "device", "OryConc"]
# RAW_DATA_HEADERS.extend([str(i) for i in range(1350, 1651)])
#
# print(RAW_DATA_HEADERS[:3])
# a = {1: 'a', 2: 'b'}
# print(a)
a = [0, 2, 3, 7, 8]


# def rolling(_list, avg_pts):
#     rolling_avg = []
#     for i in range(1, len(a)+1):
#         print(f"i = {i}, neg: {i-avg_pts}")
#
#         if (i-avg_pts) > 0:
#             print(_list[i - avg_pts:i])
#             avg = sum(_list[i - avg_pts:i]) / avg_pts
#         else:
#             print(a[:i])
#             avg = sum(_list[:i]) / i
#
#         rolling_avg.append(avg)
#         print(f"rolling avg: {rolling_avg}, {avg}")
#     return rolling_avg
#
#
# avg = rolling(a, 3)
# print(f"avg: {avg}")
