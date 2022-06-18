# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"



import requests
from bs4 import BeautifulSoup

url = 'https://support.spectralengines.com/sdk/nirone/nm-series-interface-commands/concepts/NM-series_interface_commands_FW1.0_xm_start_a_measurement_scan_xm_cr.html'
page = requests.get(url)
print(page)
with open('start_a_measurement_scan.html', 'wb+') as f:
    f.write(page.content)


