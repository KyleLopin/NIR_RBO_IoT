# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Impliment an option menu for the NIR rice bran IoT project GUI
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import json
import os
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
# local files
import global_params


class NIRMenu(tk.Menu):
    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.master = master
        self.make_filemenu()
        self.make_setting_menu()

    def make_setting_menu(self):
        setting_menu = tk.Menu(self)
        self.add_cascade(label="Settings", underline=0,
                         menu=setting_menu)
        # setting_menu.add_command(label="Rolling Avg",
        #                          command=self.change_rolling_avg)
        for device in global_params.POSITIONS.keys():
            print()
            setting_menu.add_command(label=f"Set {device} model parameters",
                                     command=lambda d=device: self.change_model(d))


    def make_filemenu(self):
        self.file_menu = tk.Menu(self)
        self.add_cascade(label="File", underline=0,
                         menu=self.file_menu)
        self.file_menu.add_command(label="Open", underline=1,
                                   command=self.open_file)
        self.file_menu.add_command(label="Exit", underline=1,
                                   command=self.master.main_destroy)

    def get_filename(self):
        try:
            script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
            rel_path = ""
            abs_file_path = os.path.join(script_dir, rel_path)
            filename = filedialog.askopenfilename(initialdir=abs_file_path)
            return filename
        except:  # suppress the error for no selection
            pass

    def open_file(self):
        filename = self.get_filename()
        # print(f"filename: {filename}")
        self.master.open_file(filename)

    def change_model(self, device):
        print(f"change model device: {device}")
        filename = self.get_filename()
        if not filename:
            return  # no name
        ref_index, coef_index, dark_index, const_index = None, None, None, None
        refs, coefs, dark = [], [], []
        constant = None
        with open(filename, 'r') as _file:
            for i, line in enumerate(_file.readlines()):
                line_split = line.split(',')
                if i == 0:
                    # check for model params in the header
                    for i, item in enumerate(line_split):
                        print(i, item, "Ref" in item)
                        if "Ref" in item or "ref" in item:
                            ref_index = i
                            print(f"ref_index = {ref_index}")
                        elif "Coef" in item or "coef" in item:
                            coef_index = i
                        elif "Cons" in item or "cons" in item:
                            const_index = i
                        elif "dark" in item or "Dark" in item:
                            dark_index = i
                else:
                    if not constant and const_index:
                        constant = float(line_split[const_index])
                    # print(line_split)
                    if ref_index:
                        refs.append(float(line_split[ref_index]))
                    if coef_index:
                        coefs.append(float(line_split[coef_index]))
                    if dark_index:
                        dark.append(float(line_split[dark_index]))
        # open sensor settings json file to change
        self.update_sensor_model(device, refs, coefs,
                                 constant, dark)
        self.master.update_model(device)

    def update_sensor_model(self, device, refs_,
                            coefs_, const_, dark_):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        if refs_:
            data[device]["Ref Intensities"] = refs_
        if coefs_:
            data[device]["Coeffs"] = coefs_
        if const_:
            data[device]["Constant"] = const_
        if dark_:
            data[device]["Dark Intensities"] = dark_
        with open("sensor_settings.json", "w") as _file:
            json.dump(data, _file)

    def change_rolling_avg(self):
        pass


class RollingTopLevel(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        tk.Label("Display rolling avg:").pack(side=tk.TOP)
