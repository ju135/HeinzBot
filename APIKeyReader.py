import json
keyFileName = "api-keys.json"


def read_telegram_key():
    f = open(keyFileName, "r")
    datastore = json.load(f)
