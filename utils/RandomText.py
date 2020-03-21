import random
import json


def get_random_string_of_messages_file(file: str, categories: [str] = None) -> str:
    """
    Returns a random string out of a json file with the format {"messages": <categorized_content>}

    :param file: The JSON file containing the data (path & name).
    :param categories: The JSON-children to navigate to the required messages.
    E.g. ["p1", "p2"] for the file {"messages": {"p1": {"p2": ["m1","m2"]}}}
    :return:
    """
    try:
        f = open(file, "r", encoding='utf-8')
    except FileNotFoundError:
        print(f"Exception in RandomText.py: File '{file}' not found.")
        return ""

    message_data = json.load(f)["messages"]

    if categories is not None:
        for category in categories:
            try:
                message_data = message_data[category]
            except KeyError:
                print(f"Exception in RandomText.py: Key '{category}' not found in file '{file}'")
                return ""

    return message_data[random.randint(0, len(message_data) - 1)]

