# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import csv
import datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id="AKIASKWLIZDDSEEZHSOM",
                          aws_secret_access_key="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",
                          region_name="ap-southeast-1")

table = dynamodb.Table('RBO_raw_data')
today = datetime.date.today().strftime('%Y-%m-%d')
today_data = table.query(
            KeyConditionExpression=Key("Date").eq(today)
        )
print(today_data)

with open("data.csv", 'w') as _file:
    writer = csv.writer(_file)

    for item in today_data["Items"]:
        time = item["Datetime"]
        # print(time)
        dec_data = item['raw_data']["Raw_data"]
        data = [float(x) for x in dec_data]
        # print(data)
        data_list = [time]
        data_list.extend(data)
        print(data_list)

        writer.writerow(data_list)
