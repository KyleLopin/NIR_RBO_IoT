# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"


from brukeropusreader import read_file

opus_data = read_file('ISI017.0')

print(f'Parsed fields: '
      f'{list(opus_data.keys())}')

print(f'Absorption spectrum: '
      f'{opus_data["AB"]}')