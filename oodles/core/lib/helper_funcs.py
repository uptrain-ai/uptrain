import json


def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)
