# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

from brukeropusreader import read_file
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn')

opus_data_F3 = read_file('RBO_F3.0')

type = "ScSm"
# type = "AB"
# type = "ScRf"
param_key = f"{type} Data Parameter"
wnum = False

print(param_key)
def norm_data(data):
    print(data)
    print(sum(data))
    print(data/sum(data))
    return data/sum(data)
    # return data/data[545]

print(opus_data_F3)
for key, value in opus_data_F3.items():
    print(key)
    print(value)
print('----')
print(opus_data_F3.keys())
print(opus_data_F3["AB"])
wavelengths = np.linspace(10000/3999, 10000/12493, len(opus_data_F3[type]))
# wavelengths = np.linspace(3999, 12493, len(opus_data_F3[type]))
for i, l in enumerate(wavelengths):
    if l > 6050 and l< 6200:
        print(i, l)
# plt.plot(wavelengths, opus_data_F3[type], label="F3")
F3 = norm_data(opus_data_F3[type])
wavelengths = opus_data_F3.get_range(spec_name=type, wavenums=wnum)
# print(len(F3), len(wavelengths))
plt.plot(wavelengths, F3, label="low")

opus_A1 = read_file('RBO_A1.0')
# plt.plot(wavelengths, opus_A1[type], label="low")
A1 = norm_data(opus_A1[type])
wavelengths = opus_A1.get_range(spec_name=type, wavenums=wnum)
plt.plot(wavelengths, A1, label="medium")

opus_A3 = read_file('RBO_A3.0')
# plt.plot(wavelengths, opus_A3[type], label="high")
A3 = norm_data(opus_A3[type])
wavelengths = opus_A3.get_range(spec_name=type, wavenums=wnum)
print('========')
print(opus_A3.get_range())
# print(opus_A3.interpolate())
plt.plot(wavelengths, A3, label="high")
print(len(opus_A3[type]))
plt.legend(title="Acid value")
# plt.xlabel("Wavenumber (cm-1)")
plt.xlabel("wave lenght (nm)")
# plt.axvline(9400, c='r', ls='--', lw=2)
# plt.axvline(7502, c='b', ls='--', lw=2)
# plt.axvline(6060, c='k', ls='--', lw=2)
# plt.axvline(7400, c='k', ls='--', lw=2)
plt.axvline(10000000/9400, c='r', ls='--', lw=2)
plt.axvline(10000000/7502, c='b', ls='--', lw=2)
plt.axvline(10000000/6060, c='k', ls='--', lw=2)
plt.axvline(10000000/7400, c='k', ls='--', lw=2)
plt.show()
