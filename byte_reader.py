# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import struct
import matplotlib.pyplot as plt

filename = "RBO_A1.0"

with open(filename, 'rb') as _f:
    data = _f.read()

print(len(data))
last_100f = data[-400:]
# print(last_100f)
# print(len(last_100f))
# print('+=============')
#
# mix_2 = data[-800:-400]
# print(mix_2)
# print(len(mix_2))
# print("88888888")
# mix_3 = data[-1200:-800]
# print(mix_3)
# print(len(mix_3))
# print("------")
# mix_3 = data[-1600:-1200]
# print(mix_3)
# print("------2")
# mix_3 = data[-2000:-1600]
# print(mix_3)
# print("------3")
# mix_3 = data[-2400:-2000]
# print(mix_3)

data_split = data.split(b"END")
for i, split in enumerate(data_split):
    print(split)
    # print(i, len(split), len(split)/4, (b"AV" in split))
    # if b"AV" in split:
    #     start = split.index(b"AV")+2
    #     print('----------')
    #     # print(start)
    #     print(split)
        # print(split[start:start+40])
        # f_s = struct.unpack('>ffffffffff', split[start:start+40])
        # print(':::::', f_s)
    # if i == 13:
    #     print('------')
    #     print(len(split[5:])/4)
    #     data = struct.unpack(2932*"f", split[5:])
    #     plt.plot(data[:2000])
    #     plt.show()
