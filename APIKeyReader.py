import json

keyFileName = "api-keys.json"


def read_key(key_name) -> str:
    f = open(keyFileName, "r")
    key_data = json.load(f)
    try:
        data = key_data[key_name]
        return data
    except:
        print(key_name + " not found")
        return ""
