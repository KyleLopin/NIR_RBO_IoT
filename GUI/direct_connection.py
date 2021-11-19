# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import re
import socket
import subprocess

import data_class


class DirectConnection:
    def __init__(self, master, data=None):
        # if data:
        #     self.data = data
        # else:
        #     self.data = data_class.TimeStreamData()
        self.find_pis()

    def find_pis(self):
        arpa = subprocess.check_output(("arp", "-a")).decode("ascii")
        print(arpa)
        for line in arpa.split("\n"):
            print("-----")
            print(line)
            ip_addr = line.split("(")[1].split(")")[0]
            print(ip_addr)
            if "B8:27:EB" in line:  #
                print("looking for pi 3 from ipv6")
                self.try_connect(ip_addr)
            elif "192.168.1" in line:
                print("looking for pi 3 from ipv4")
                self.try_connect(ip_addr)
            elif "dc:a6:32" in line:  # raspberry pi 4
                print("looking for pi 4 from ipv6")
                self.try_connect(ip_addr)

    def try_connect(self, ip_address):
        # command = f"ping -c 1 {ip_address}"
        command = ['ping', '-c', '1', '-S', ip_address]
        print(f"command: {command}")
        response = subprocess.call(command)
        print('++++++++')
        print(f"response: {response}")
        pass  # asgard


if __name__ == "__main__":
    DirectConnection(None)
