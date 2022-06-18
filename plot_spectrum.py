# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"


import matplotlib.pyplot as plt
import pandas as pd


data = pd.read_csv("data.csv")

spectrum = data.iloc[:,1:]
print(spectrum)
spectrum.T.plot()
plt.show()
