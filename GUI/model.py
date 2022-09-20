# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import json
import os

# installed libraries
import numpy as np
# import pandas as pd

# local files
import global_params

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


DEVICES = global_params.DEVICES


class Models:
    def __init__(self, devices):
        # open json file to get model params
        with open(os.path.join(__location__, "new_models.json"), "r") as _file:
            json_data = json.load(_file)
        # print("model data")
        # print(json_data)
        self.models = dict()
        for device in devices:
            # print(f"device_number: {device_number}")
            # print(json_data[device_number])
            # for key in json_data[device_number].keys():
            #     print(f"{key}, {len(json_data[device_number][key])}")
            #     print(f"{json_data[device_number][key]}")
            self.models[device] = Model(json_data[device])

    def fit(self, raw_data, device):
        return self.models[device].fit(raw_data)


class Model:
    def __init__(self, model_params):
        # print("make model")
        # print(model_params.keys())
        # print(model_params["abs_signal_processes"])
        self.constant = np.array(model_params["Constant"])
        self.dark = np.array(model_params["Dark Intensities"])
        self.ref = np.array(model_params["Ref Intensities"])
        self.ref_minus_dark = self.ref - self.dark
        # print(self.ref_minus_dark)
        self.coeffs = np.array(model_params["Coeffs"])
        self.raw_signal_process = None
        self.refl_signal_process = None
        self.abs_signal_process = None
        if "raw_signal_process" in model_params:
            self.raw_signal_process = model_params["raw_signal_process"]
        if "refl_signal_process" in model_params:
            self.refl_signal_process = model_params["refl_signal_process"]
        if "abs_signal_process" in model_params:
            # print("setting abs signal")
            self.abs_signal_process = model_params["abs_signal_process"]

    def fit(self, raw_data):
        # print(f"Fit: {len(raw_data)}, {self.raw_signal_process}")

        raw_data = np.array(raw_data)
        # print(raw_data.shape)
        if self.raw_signal_process:
            raw_data = self.fit_signal_processes(raw_data, self.raw_signal_process)
        # print(len(raw_data), len(self.dark), len(self.ref_minus_dark))
        # print(type(raw_data), type(self.dark), type(self.ref_minus_dark))
        # print(type(raw_data[0]), type(self.dark[0]), type(self.ref_minus_dark[0]))
        
        refl_data = (raw_data-self.dark) / self.ref_minus_dark
        # print('procss: ', self.refl_signal_process)
        if self.refl_signal_process:
            refl_data = self.fit_signal_processes(refl_data, self.refl_signal_process)
        abs_data = -np.log10(refl_data)
        # print(abs_data)
        # print(type(abs_data))
        # for x in abs_data:
        #     print(x)
        abs_data = np.array([0 if np.isnan(x) else x for x in abs_data])
        # print('kl', len(abs_data))
        # print(self.abs_signal_process)
        if self.abs_signal_process:
            abs_data = self.fit_signal_processes(abs_data, self.abs_signal_process)
        # print(f"abs data len: {abs_data.shape}")
        # print(f"coefs len: {self.coeffs.shape}")
        # print(self.constant)
        if self.coeffs.shape[0] > abs_data.shape[0]:
            print(len(self.coeffs[:abs_data.shape[0]]))
            self.coeffs = self.coeffs[:abs_data.shape[0]]
            print("trimmed")
        final_array = abs_data * self.coeffs
        conc = final_array.sum() + self.constant
        # print(f"type conc: {conc}, {type(conc)}")
        if type(conc) is list:
            conc = conc[0]
        return float(final_array.sum() + self.constant)

    def fit_signal_processes(self, data, processes):
        # print(f"processing: {processes}")
        for process in processes:
            # print(f"process: {process}")
            # print(f"l{process[0]}l")
            # print(process[0] == "SG")
            if process[0] == "SNV":
                data = snv(data)
            if process[0] == "SG":
                # print("SG process")
                params = process[1]
                data = savitzky_golay(data,
                                      params["window"],
                                      params["polyorder"],
                                      deriv=params["deriv"])
        return data


# from scipy cookbook
def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial
    try:
        window_size = np.abs(int(window_size))
        order = np.abs(int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    # firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    # lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    # y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


# from https://nirpyresearch.com/two-scatter-correction-techniques-nir-spectroscopy-python/
def snv(input_data):
    # Define a new array and populate it with the corrected data
    output_data = np.zeros_like(input_data)
    # print(input_data.shape)
    output_data = (input_data - np.mean(input_data)) / np.std(input_data)

    # for i in range(input_data.shape[0]):
    #     # Apply correction
    #     output_data[i, :] = (input_data[i, :] - np.mean(input_data[i, :])) / np.std(input_data[i, :])

    return output_data


if __name__ == "__main__":
    # r = savitzky_golay(np.array([1, 2, 9, 4, 5, 9, 7, 8, 15, 10]),
    #                   5, 0)
    # print(r)
    ml_models = Models(["device_1",
                        "device_2",
                        "device_3", "AV"])
    array = [1000 for i in range(301)]

    # data = pd.read_excel("Models_saved.xlsx",
    #                      sheet_name="Crude")
    # array = data.iloc[3:4, 5:].values.tolist()[0]
    # # array = array.reshape(1, -1)
    # print("===")
    # print(array)
    # # print(array.shape)
    #
    # print(len(array))
    # result = ml_models.fit(array, "AV")
    # print(result)
