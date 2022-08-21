import json
import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_json(file):
    json_data = open(os.path.join(__location__, file)).read()
    json_settings = json.loads(json_data)
    return json_settings


data = get_json("new_models.json")
print(data.keys())
for key in data:
    print(f"key: {key}")
    # print(f"value: {data[key]}")
    
    for key2 in data[key]:
        print(f"keys: {key2}")
        print(f"values: {data[key][key2]}")
    
