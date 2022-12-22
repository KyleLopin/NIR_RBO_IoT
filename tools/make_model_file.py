# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Make a new new_model.json file to upload to the sensor when
new data is fitted

The models are saved in the sensor_models.json with a structure:
{ "device_1": {"Dark Intensities": [...],
               "Ref Intensities": [...],
               "models": {"Ory": {"Constant": [.],
                                  "Coeffs": [...],
                                  "abs_signal_process: [...]},
                          "AV": {"Constant": [.],
                                 "Coeffs": [...],
                                 "abs_signal_process: [...]}
                          }
               },
  "device_2": .... etc.
}
"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import json

# installed libraries
import pandas as pd

MODELS = {"device_1": ["Ory", "AV"],
          "device_2": ["Ory", "AV"],
          "device_3": ["Ory"]
          }
TREATMENT = {"device_1": {"Ory": [['SG', {'deriv': 1, 'polyorder': 2, 'window': 21}]],
                          "AV": [['SNV']]
                          },
             "device_2": {"Ory": [['SG', {'deriv': 1, 'polyorder': 2, 'window': 21}]],
                          "AV": [['SNV']]
                          },
             }
FILENAME_MAP = {"device_1": "Sensor1_Crude.xlsx",
                "device_2": "Sensor2_Neutralized.xlsx",
                "device_3": "Sensor3_Deodorized.xlsx"
                }
SHEETNAME_MAP = {"device_1": "Sensor1_Crude",
                 "device_2": "Sensor2_Neutralized",
                 "device_3": "Sensor3_Deodorized"
                 }
ALL_WAVELENGTHS = list(range(1350, 1651))
ZEROS = list(range(1350, 1651))
WINDOW_WAVELENGTHS = list(range(1360, 1641))


def view_file():
    """ View each """
    with open("old_models.json", 'r', encoding='utf-8') as _file:
        json_data = json.load(_file)
    for key in json_data.keys():
        print(key)
        for key2 in json_data[key].keys():
            print('==', key, key2)
            print(json_data[key][key2])


def get_ref_values(device: str) -> list[float]:
    """
    Get the reference values of a device from the Excel file.

    Args:
        device (str): name of the device, ie "device_1"

    Returns: list of floats of the reference light values

    """
    data = pd.read_excel("Reference Values.xlsx",
                         sheet_name=SHEETNAME_MAP[device])
    return data["Intensity"].values.tolist()


def get_coeffs_into_list(data_frame, use_filter=False) -> list:
    """
    Take in a data frame with wavelengths as the index and
    model coefficients in the 'coeffs' column and make a list of the
    coefficients, but not all wavelengths may be present in the
    index as variable selection could have been preformed on
    the model so put 0 in if there is a missing wavelength.
    Use the ALL_WAVELENGTHS for data that is not using an SG filter
    Use the WINDOW_WAVELENGTHS for data with a 21 window SG filter

    Args:
        data_frame (pd.DataFrame): data frame with wavelengths in the first column
            and the coefficients in the second, may be missing wavelengths
        use_filter (bool): boolean to see if a 21 window SG filter is being
            used so a shortened number of wavelength coefficients should be sent
            back

    Returns: list of the coefficients of the proper length

    """
    coeffs = []
    wavelengths = ALL_WAVELENGTHS
    if use_filter:
        wavelengths = WINDOW_WAVELENGTHS
    for wavelength in wavelengths:
        # print(f"test: {wavelength}, {wavelength in df.index}")
        if wavelength in data_frame.index:
            coeffs.append(data_frame.loc[wavelength, "coeffs"])
        else:
            coeffs.append(0)
    return coeffs


def make_model_dict(device: str, model: str) -> dict:
    """
    Make a dictionary for a model with the keys: Constant,
    coeffs, and abs_signal_process. Dark and reference intensities
    are in the sensor level.

    Args:
        device (str): which device it is, ie "device_1", etc.
        model (str): which model, "Ory" or "AV"

    Returns: dictionary with the keys of Constant, coeffs, and possibly
        abs_signal_process

    """
    new_model = {}
    filename = FILENAME_MAP[device]
    print(f"make model for {device}, {model}, {filename}")
    # excel_file = pd.ExcelFile(filename)
    data = pd.read_excel(filename, sheet_name=model,
                         header=None)
    # Get the constant for the model
    new_model["Constant"] = data.iloc[0, 1]

    # add the treatment options
    treatment = []
    if device in TREATMENT:
        # print(f"device: {TREATMENT[device]}")
        if model in TREATMENT[device]:
            treatment = TREATMENT[device][model]
            print(f"treatment: {treatment}")
            new_model['abs_signal_process'] = treatment

    # Get coeffs, need to know if an SG filter is used
    use_filter = False
    print(treatment, len(treatment))
    if len(treatment) > 0:
        if 'SG' in treatment[0]:
            use_filter = True
    # convert the df to get the coeffs out later
    coeff_df = data.iloc[1:, :]
    coeff_df.columns = ["wavelengths", "coeffs"]
    coeff_df = coeff_df.set_index("wavelengths")
    # print(f"using filter: {use_filter}, {treatment}")
    new_model["Coeffs"] = get_coeffs_into_list(coeff_df, use_filter)
    # print(f"new model: {device}, {model}, {new_model}")
    return new_model


def make_new_file():
    """
    Make a new file with all the sensor models in it, the structure is in the
    file doc string
    """
    new_file = {}
    for device, models in MODELS.items():
        new_file[device] = {}
        # get sensor info, ie Dark and reference intensities
        new_file[device]["Dark Intensities"] = ZEROS
        new_file[device]["Ref Intensities"] = get_ref_values(device)
        new_file[device]["models"] = {}
        # models = MODELS[device]
        print(f"device: {device}, models: {models}")
        for model in models:
            new_file[device]["models"][model] = make_model_dict(device, model)
    print(new_file)
    with open("sensor_models.json", 'w', encoding='utf-8') as _file:
        _file.write(json.dumps(new_file, sort_keys=True, indent=4))


def view_new_file():
    """ Pretty print out the sensor_models.json file """
    with open("sensor_models.json", 'r', encoding='utf-8') as _file:
        json_data = json.load(_file)
    for key in json_data.keys():
        print(key)
        for key2 in json_data[key].keys():
            print('    ', key, key2)
            if key2 == "models":
                for model in json_data[key][key2].keys():
                    print('        ', model)
                    print('            ', json_data[key][key2][model])
            else:
                print('        ', json_data[key][key2])


if __name__ == '__main__':
    # view_file()
    make_new_file()
    view_new_file()
