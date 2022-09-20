# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Hold a class that deals with communicating with a remote IoT sensor
and update any settings / models they have

NOTE: Most of these are not tested adequately, they were
made redundant by using local models and fixing the settings.
These would be nice to have when there is time to check them
"""

__author__ = "Kyle Vitatus Lopin"

# standard libraries
import json

# local files
import global_params

# CONSTANTS
MODEL_KEYS = ["Constant", "Coeffs", "Ref Intensities",
              "Dark Intensities"]
DEVICES = global_params.DEVICES.keys()
POSITIONS = global_params.POSITIONS


class SensorChecker:
    def __init__(self, _comm_channel, _data):
        self.communication = _comm_channel
        self.data = _data

    def get_model_params(self, device):
        """
        Ask for the devices model parameters.  These will be received by
        the on_message callback, which has to send the data to the check_model
        module for confirmation

        Args:
            device (str): string of the device number to ask the data for

        Returns:  None, the sensor will respond, that is received by the
        on_message callback of the communications channel

        """
        device_topic = f"device_number/{device}/control"
        pkt = '{"command": "send model"'
        self.communication.publish(device_topic, pkt, qos=0)

    def check_model(self, position, sensor_model):
        """
        After the sensor was asked to send the model params, the
        sensor will respond with the params.  The on_message callback
        needs to call this method to check the model params

        Args:
            position (str):  position of the device, ie "position 2"
            sensor_model (dict): model parameters, keys are type of values,
            ie.

        Returns:

        """
        # get the stored model
        with open("new_models.json", "r") as _file:
            data = json.load(_file)
        data = data[position]
        print(f"Master model params:")
        for key in MODEL_KEYS:
            print(key)
            print(data[key])
            if data[key] != sensor_model[key]:
                return False
        # if all data and sensor models are the same,
        # everything is all good, hopefully
        # TODO: the JSON file needs to be updated so replace device with position
        device = global_params.POSITIONS[position]
        print("Model correct")
        if device in self.data.devices:
            self.data.devices[device].model_checked = True
            return True
        return False  # no device_number

    def ask_for_model(self, device_number):
        _topic = f"device/{device_number}/control"
        _message = '{"command": "send model"}'
        self.communication.publish(_topic, _message, qos=0)

    def check_settings(self, position, sensor_model):
        # get the stored model
        with open("sensor_settings.json", "r") as _file:
            data = json.load(_file)
        data = data[position]
        print(f"Master model params:")
        for key in MODEL_KEYS:
            print(key)
            print(data[key])
            # if data[key] != sensor_model[key]:
            #     return False
        # if all data and sensor models are the same,
        # everything is all good, hopefully
        device = global_params.POSITIONS[position]
        print("Model correct")
        if device in self.data.devices:
            self.data.devices[device].model_checked = True
            return True
        return False  # no device_number

    def ask_for_settings(self, position):
        device = DEVICES[position]
        _topic = f"device_number/{device}/control"
        _message = '{"command": "send sensor settings"}'
        self.communication.publish(_topic, _message, qos=1)

    def update_models(self):
        for position in POSITIONS:
            self.update_model(position)

    def update_model(self, device):
        with open("new_models.json", "r") as _file:
            data = json.load(_file)
        if device not in data:
            return
        device_data = data[device]

        device_topic = f"device_number/{global_params.POSITIONS[device]}/control"
        update_pkt = {"command": "update model"}
        for key in device_data.keys():
            update_pkt[key] = device_data[key]
        pkt = json.dumps(update_pkt)
        self.communication.publish(device_topic, pkt, qos=0)
        print("Done with model")


if __name__ == "__main__":
    sensor_check = SensorChecker(None, None)
    sensor_check.check_settings("position 2", None)
