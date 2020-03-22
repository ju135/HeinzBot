import json
from abc import ABC

from telegram import Update


class AbstractModule(ABC):
    mutedAccounts = list()
    _commandList = ""
    keyFileName = "api-keys.json"

    def get_chat_id(self, update: Update):
        return update.message.chat_id

    def add_help_text(self, text):
        AbstractModule._commandList += text

    def get_api_key(self, key_name):
        f = open(self.keyFileName, "r")
        key_data = json.load(f)
        try:
            data = key_data[key_name]
            return data
        except:
            print(key_name + " not found")
            return ""

    def has_rights(self, update):
        if update.message.from_user.name in self.mutedAccounts:
            update.message.reply_text(
                '..hot wer wos gsogt?')
            return False
        if update.message.from_user.last_name in self.mutedAccounts:
            update.message.reply_text(
                '..hot wer wos gsogt?')
            return False
        return True

    def get_command_parameter(self, command: str, update) -> str:
        text = update.message.text
        b = update.message.bot.name
        if text.startswith(command + " "):
            return text[len(command) + 1:]
        if text.startswith(command + b + " "):
            return text[len(command + b) + 1:]
