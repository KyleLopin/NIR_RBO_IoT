# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

from brukeropusreader import read_file
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import white_tophat, black_tophat
import skimage.morphology
# from skimage.filters.rank import tophat

plt.style.use('seaborn')


def norm_data(data):
    print(data)
    print(sum(data))
    print(data/sum(data))
    return data/sum(data)


type = "ScSm"
# type = "AB"
# type = "ScRf"
wnum = False

opus_data_F3 = read_file('RBO_F3.0')
F3 = norm_data(opus_data_F3[type])

wavelengths = opus_data_F3.get_range(spec_name="ScSm", wavenums=wnum)

# plt.plot(wavelengths, opus_data_F3["ScSm"], label="ScSm")
# wavelengths = opus_data_F3.get_range(spec_name="ScSm", wavenums=wnum)
# plt.plot(wavelengths, opus_data_F3["ScRf"], label="ScRf")
# plt.plot(wavelengths, F3, label="low")

top_ = black_tophat(opus_data_F3["ScSm"], np.array(500*[1]))
diff = opus_data_F3["ScSm"]+top_
#
# diff = opus_data_F3["ScSm"] - top_

def black_hat(filename):
    print(filename)
    data = read_file(filename)
    wavelengths = data.get_range(spec_name="ScSm", wavenums=wnum)
    top_data = black_tophat(data["ScSm"], np.array(500*[1]))
    return wavelengths, top_data


w1, t1 = black_hat('RBO_F3.0')
w2, t2 = black_hat('RBO_A1.0')
w3, t3 = black_hat('RBO_A3.0')
plt.plot(w1, t1, label='low')
plt.plot(w2, t2, label='medium')
plt.plot(w3, t3, label='high')
plt.xlabel("wave lenght (nm)")
plt.legend(title="Method")
plt.title("Black tophat")

# plt.plot(wavelengths, top_, label='tophat')
# plt.plot(wavelengths, diff, label='black tophat')
plt.axvline(10000000/9400, c='r', ls='--', lw=2)
plt.axvline(10000000/7502, c='b', ls='--', lw=2)
plt.axvline(10000000/6060, c='k', ls='--', lw=2)
plt.axvline(10000000/7400, c='k', ls='--', lw=2)


plt.legend()
plt.show()
