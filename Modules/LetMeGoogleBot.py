import json
import requests
import telegram
from APIKeyReader import read_key

base_url = "https://de.lmgtfy.com/"


def create_google_request(bot, update):
    query1 = get_command_parameter("/google", update)
    query2 = get_command_parameter("/ya", update)
    query3 = get_command_parameter("/ddg", update)

    if query1 is not None:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query1)

    if query2 is not None:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query2 + "&s=y&t=w")

    if query3 is not None:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query3 + "&s=d&t=w")


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command + " "):
        return text[len(command) + 1:]
    if text.startswith(command + b + " "):
        return text[len(command + b) + 1:]
