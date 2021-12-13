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

MIN_SCAN_BUFFER = 5
NUMBER_WAVELENGTHS = 301


class NIRMenu(tk.Menu):
    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.master = master
        self.make_filemenu()
        self.make_setting_menu()
        self.make_local_setting_menu()
        # self.make_update_menu()

    def make_local_setting_menu(self):
        local_setting_menu = tk.Menu(self)
        self.add_cascade(label="Settings", underline=0,
                         menu=local_setting_menu)
        local_setting_menu.add_cascade(label="Change rolling average",
                                       command=lambda m=self.master: RollingTopLevel(m))

    def make_update_menu(self):
        update_menu = tk.Menu(self)
        self.add_cascade(label="Update remote data",
                         menu=update_menu)
        update_menu.add_cascade(label="Check for remote data",
                                command=self.master.get_remote_data)

    def make_setting_menu(self):
        setting_menu = tk.Menu(self)
        self.add_cascade(label="Sensor Settings", underline=0,
                         menu=setting_menu)
        # setting_menu.add_command(label="Rolling Avg",
        #                          command=self.change_rolling_avg)
        for device in global_params.POSITIONS.keys():
            setting_menu.add_command(label=f"Update {device} model [Load file]",
                                     command=lambda d=device: self.change_model(d))
        setting_menu.add_separator()
        for device in global_params.POSITIONS.keys():
            setting_menu.add_command(label=f"Set {device} model settings",
                                     command=lambda d=device: self.change_model_settings(d))

        setting_menu.add_separator()
        for device in global_params.POSITIONS.keys():
            setting_menu.add_command(label=f"Set {device} scan parameters",
                                     command=lambda d=device: self.change_scan_params(d))

    def make_filemenu(self):
        self.file_menu = tk.Menu(self)
        self.add_cascade(label="File", underline=0,
                         menu=self.file_menu)
        self.file_menu.add_command(label="Open", underline=1,
                                   command=self.open_file)

        self.file_menu.add_separator()
        for _type in ["Oryzanol", "Temperature"]:
            save_menu = tk.Menu(self.file_menu)
            self.file_menu.add_cascade(label=f"Save {_type} Data", menu=save_menu)
            for device in global_params.POSITIONS.keys():
                save_menu.add_command(label=f"Save {device} data",
                                      command=lambda d=device, t=_type: self.save_data(d, t))
            self.file_menu.add_separator()

        self.file_menu.add_command(label="Exit", underline=1,
                                   command=self.master.main_destroy)

    def save_data(self, position, data_type):
        print(f"saving device: {position} data")
        self.master.save_data(data_type, global_params.POSITIONS[position])

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
        # print(f"change model device: {device}")
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
                        # print(i, item, "Ref" in item)
                        if "Ref" in item or "ref" in item:
                            ref_index = i
                            # print(f"ref_index = {ref_index}")
                        elif "Coef" in item or "coef" in item:
                            coef_index = i
                        elif "Cons" in item or "cons" in item:
                            const_index = i
                        elif "dark" in item or "Dark" in item:
                            dark_index = i
                else:
                    if not constant and const_index:
                        # once constant is set this will stop calling
                        constant = float(line_split[const_index])
                    # print(line_split)
                    if ref_index:
                        refs.append(float(line_split[ref_index]))
                    if coef_index:
                        coefs.append(float(line_split[coef_index]))
                    if dark_index:
                        dark.append(float(line_split[dark_index]))

        # do error checking
        data_ok = True
        if ref_index and len(refs) != NUMBER_WAVELENGTHS:
            messagebox.showerror("Error in model file",
                                 (f"Need 301 data points for reference "
                                  f"got {len(refs)}\n"
                                  f"NOT UPDATING MODEL, PLEASE FIX DATA FILE"))
            data_ok = False
        if coef_index and len(coefs) != NUMBER_WAVELENGTHS:
            messagebox.showerror("Error in model file",
                                 (f"Need 301 data points for coefficients "
                                  f"got {len(refs)}\n"
                                  f"NOT UPDATING MODEL, PLEASE FIX DATA FILE"))
            data_ok = False
        if dark_index and len(dark) != NUMBER_WAVELENGTHS:
            messagebox.showerror("Error in model file",
                                 (f"Need 301 data points for dark currents "
                                  f"got {len(refs)}\n"
                                  f"NOT UPDATING MODEL, PLEASE FIX DATA FILE"))
            data_ok = False

        if not data_ok:
            return  # don't save or send, model is all jacked up

        # open sensor models json file to change
        self.update_sensor_model(device, refs, coefs,
                                 constant, dark)
        self.master.update_model(device)

    def update_sensor_model(self, device, refs_,
                            coefs_, const_, dark_):
        with open("models.json", "r") as _file:
            data = json.load(_file)
        if refs_:
            data[device]["Ref Intensities"] = refs_
        if coefs_:
            data[device]["Coeffs"] = coefs_
        if const_:
            data[device]["Constant"] = const_
        if dark_:
            data[device]["Dark Intensities"] = dark_
        with open("models.json", "w") as _file:
            json.dump(data, _file)

    def change_model_settings(self, device):
        ChangeModelParams(self.master, device)

    def change_rolling_avg(self):
        pass

    def change_scan_params(self, device):
        print(f"changing scan paremeters for {device}")
        ChangeScanParams(self.master, device)


class ChangeModelParams(tk.Toplevel):
    def __init__(self, master, device):
        tk.Toplevel.__init__(self, master)
        self.geometry("350x350")
        self.title = "Set Model settings"
        self.master = master
        self.device = device

        saved_settings = self.get_params(device)
        print(f"saved settings: {saved_settings}")

        # make signal processing options
        self.snv_var = tk.BooleanVar()
        self.snv_var.set(saved_settings["use_snv"])
        tk.Checkbutton(self, text="Use SNV scatter correction",
                       variable=self.snv_var,
                       onvalue=True, offvalue=False).pack()

        tk.Label(self, text=("Note: The Savitzky–Golay smoothing filter\n"
                             "will be applied before the Standard Normal\n"
                             "Variate scatter correction")).pack()

        self.sg_var = tk.BooleanVar()
        self.sg_var.set(saved_settings['use_sg'])
        tk.Checkbutton(self, text="Use Savitzky–Golay smoothing filter",
                       variable=self.sg_var,
                       onvalue=True, offvalue=False,
                       command=self.sg_change).pack()

        tk.Label(self, text="SG filter window").pack()
        window_values = [2*i+1 for i in range(25)]
        self.sg_window = tk.IntVar()
        self.sg_window_spin = tk.Spinbox(self, values=window_values,
                                         textvariable=self.sg_window,
                                         from_=1, to=50)
        self.sg_window.set(saved_settings["sg_window"])
        self.sg_window_spin.pack()

        tk.Label(self, text="SG filter polynomial order").pack()
        self.sg_polyorder = tk.IntVar()
        self.sg_polyorder_spin = tk.Spinbox(self,
                                            textvariable=self.sg_polyorder,
                                            from_=0, to=7)
        self.sg_polyorder.set(saved_settings["sg_polyorder"])

        self.sg_polyorder_spin.pack()

        tk.Label(self, text="SG filter derivative").pack()
        self.sg_deriv = tk.IntVar()
        self.sg_deriv_spin = tk.Spinbox(self,
                                        textvariable=self.sg_deriv,
                                        from_=0, to=2)
        self.sg_deriv.set(saved_settings["sg_deriv"])
        self.sg_deriv_spin.pack()
        self.sg_change()  # update if the spinbox should be active

        button_frame = tk.Frame(self)
        tk.Button(button_frame, text="Submit",
                  command=self.submit).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel",
                  command=self.exit).pack(side=tk.RIGHT)

        button_frame.pack()

    def get_params(self, device):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        return data[device]

    def sg_change(self):
        print(f"sg var: {self.sg_var.get()}")
        if self.sg_var.get():
            for element in [self.sg_window_spin,
                            self.sg_polyorder_spin,
                            self.sg_deriv_spin]:
                element.config(state=tk.NORMAL)
        else:
            for element in [self.sg_window_spin,
                            self.sg_polyorder_spin,
                            self.sg_deriv_spin]:
                element.config(state=tk.DISABLED)

    def submit(self):
        # save data to json file
        self.save_params()
        # send data to sensor
        self.master.check_sensor_settings(self.device)

    def save_params(self):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        data[self.device]["use_snv"] = self.snv_var.get()
        print(data["use_snv"])
        data[self.device]["use_sg"] = self.sg_var.get()
        data[self.device]["sg_window"] = self.sg_window.get()
        data[self.device]["sg_polyorder"] = self.sg_polyorder_spin.get()
        data[self.device]["sg_window"] = self.sg_window.get()
        with open("sensor_settings.json", "w") as _file:
            json.dump(data, _file)
            print(f"wrote file to {self.device} {data}")
        self.exit()

    def exit(self):
        self.destroy()


class ChangeScanParams(tk.Toplevel):
    def __init__(self, master, device):
        tk.Toplevel.__init__(self, master)
        self.geometry("300x300")
        self.title = "Set Scan parameters"
        self.master = master
        # self.device = global_params.POSITIONS[device]
        self.device = device
        print(f"got deviec in scan params: {self.device}")
        avg_points, avg_scan, interval = self.get_params(device)
        tk.Label(self, text="Set how many averages per point to use:").pack()
        self.pt_var = tk.IntVar()
        self.pt_var.set(avg_points)
        tk.Spinbox(self, from_=1, to=500, width=10,
                   textvariable=self.pt_var,
                   command=self.update_interval).pack()
        tk.Label(self, text="Set the number of scan averages").pack()

        self.scan_var = tk.IntVar()
        self.scan_var.set(avg_scan)
        tk.Spinbox(self, from_=1, to=150, width=15,
                   textvariable=self.scan_var,
                   command=self.update_interval).pack()
        self.min_interval_label = tk.Label(self, text=f"minimum interval = {self.calc_min_interval()} seconds")
        self.min_interval_label.pack()

        self.pt_var.trace_add("write", self.update_interval)
        self.scan_var.trace_add("write", self.update_interval)

        self.interval = tk.IntVar()
        self.interval.set(interval)
        tk.Spinbox(self, from_=5, to=300, width=15,
                   textvariable=self.interval).pack()

        self.aws_var = tk.IntVar()
        tk.Checkbutton(self, text="Use AWS server",
                       variable=self.aws_var,
                       onvalue=1, offvalue=0, width=15)

        self.aws_raw_var = tk.IntVar()
        tk.Checkbutton(self, text="Send AWS raw data",
                       variable=self.aws_raw_var,
                       onvalue=1, offvalue=0, width=15)

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM)
        tk.Button(button_frame, text="Submit", width=15,
                  command=lambda d=device: self.submit(d)).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Exit", width=15,
                  command=self.exit).pack(side=tk.RIGHT)

    def get_params(self, device):
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        data = data[device]
        pt_avg = data["pt_avg"]
        scan_avg = data["scan_avg"]
        interval = data["interval"]
        return pt_avg, scan_avg, interval
    
    def update_interval(self, *args):
        self.min_interval_label.config(text=f"minimum interval = {self.calc_min_interval()} seconds")
        self.interval.set(self.calc_min_interval())

    def calc_min_interval(self):
        # if user starts typing, it send empty string so return 0
        try:
            self.scan_var.get()
            self.pt_var.get()
        except:
            return "error"
        return int(0.01*self.scan_var.get()*self.pt_var.get()+MIN_SCAN_BUFFER)

    def submit(self, device):
        # device = global_params.POSITIONS[device]
        print(f"submitting values {self.pt_var.get()} and {self.scan_var.get()}")
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        pt_avg = self.pt_var.get()
        if pt_avg > 5 and pt_avg < 500:
            data[device]["pt_avg"] = pt_avg
        else:
            messagebox.showerror("Point Avgerage Error",
                                 "Point scan has to be between 5 and 500")
            return
        print(f"data1: {data}")
        scan_avg = self.scan_var.get()
        if 5 < scan_avg < 150:
            print(f"setting scan avg: {scan_avg}, '{device}''")
            print(data[device])
            data[device]["scan_avg"] = scan_avg
            print(data[device])

        else:
            messagebox.showerror("Point Avgerage Error",
                                 "Point scan has to be between 5 and 150")
            return

        print(f"data2: {data}")
        interval = self.interval.get()
        min_interval = self.calc_min_interval()
        if interval >= min_interval:
            data[device]["interval"] = interval
        else:
            messagebox.showerror("Interval Error",
                                 f"Interval has to be more than {min_interval}")

        print("Sending scan parameters")
        with open("sensor_settings.json", "w") as _file:
            json.dump(data, _file)
            print(f"write file {data}")
        self.master.change_scan_params(self.device,
                                       data[device])
    
    def exit(self):
        self.destroy()


class ChangeNetworkParams(tk.Toplevel):
    def __init__(self, master, device):
        tk.Toplevel.__init__(self, master)
        self.geometry("300x300")
        self.title = "Set Scan parameters"
        self.master = master
        self.device = device


class RollingTopLevel(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.master = master
        tk.Label(self, text="Display rolling avg:").pack(side=tk.TOP)
        self.roll_avg_spin = tk.Spinbox(self, command=self.update_roll,
                                        from_=1, to=150)
        self.roll_avg_spin.pack()
        button_frame = tk.Frame(self)
        # tk.Button(button_frame, text="Submit",
        #           command=self.submit).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel",
                  command=self.exit).pack(side=tk.RIGHT)

        button_frame.pack()

    def update_roll(self):
        print(f"new roll: {self.roll_avg_spin.get()}")
        self.master.data.update_rolling_samples(self.roll_avg_spin.get())

    def exit(self):
        self.destroy()

if __name__ == "__main__":
    app = tk.Tk()
    RollingTopLevel(app)
    app.mainloop()
