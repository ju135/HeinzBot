import json
import logging
from abc import ABC
from datetime import date
from repository.database import Database

from telegram import Update, ChatAction
from telegram.ext import CallbackContext
import telegram

BOT_LOGGER = 'BotLogger'


class AbstractModule(ABC):
    mutedAccounts = []
    _commandList = []
    keyFileName = "api-keys.json"

    def get_chat_id(self, update: Update):
        return update.message.chat_id

    def add_help_text(self, command: str, short_desc: str, long_desc: str, usage: [str]):
        AbstractModule._commandList.append({"command": command, "short_desc": short_desc,
                                            "long_desc": long_desc, "usage": usage})

    def log(self, text, logging_type):
        bot_logger = logging.getLogger(BOT_LOGGER)
        bot_logger.log(level=logging_type, msg=" ######## " + type(self).__name__ + " ######## " + text)

    def get_api_key(self, key_name):
        f = open(self.keyFileName, "r")
        key_data = json.load(f)
        try:
            data = key_data[key_name]
            return data
        except:
            print(key_name + " not found")
            return ""

    def get_command_parameter(self, command: str, update) -> str:
        text = update.message.text
        b = update.message.bot.name
        if text.startswith(command + " "):
            return text[len(command) + 1:]
        if text.startswith(command + b + " "):
            return text[len(command + b) + 1:]

    def percent_encoding(self, text: str) -> str:
        """
        Encode the text into an url-transferable format.
        :param text: The text to encode
        :return: the encoded text
        """
        result = ''
        accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
        for char in text.encode('utf-8'):
            result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
        return result

    def escape_markdown_characters(self, text):
        """
        Escape special characters for Markdown in a given text.
        :param text: The text to encode
        :return: the encoded text
        """

        text = text.replace("-", "\-").replace(".", "\.").replace("!", "\!").replace("(", "\(").replace(")", "\)") \
            .replace("+", "\+").replace("`", "\`").replace("*", "\*").replace("_", "\_").replace("{", "\{") \
            .replace("}", "\}").replace("[", "\[").replace("]", "\]").replace("#", "\#")

        return text

    def downsize_dash_link(self, dash_link: str, maximum_size: int) -> str:
        resolution = int(dash_link[dash_link.rindex('DASH_') + 5:].split('?')[0].split('.')[0])
        if resolution > maximum_size:
            return dash_link.replace(f"DASH_{resolution}", f"DASH_{maximum_size}")
        return dash_link

    def save_media(self, update: Update, message,
                   command: str, query: str, type: str):

        Database.instance().insert_into_media(chat_id=message.chat_id,
                                              message_id=message.message_id,
                                              command=command,
                                              username=update.message.chat.username,
                                              user_id=update.message.from_user.id,
                                              type=type,
                                              searchtext=query)

    def send_and_save_picture(self, update: Update, context: CallbackContext, image_url: str, caption: str,
                              command: str):
        chat_id = update.message.chat_id
        query = self.get_command_parameter(command=command, update=update)

        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        message = context.bot.send_photo(chat_id=chat_id, photo=image_url, caption=caption)
        self.save_media(update=update, command=command, type="image", query=query, message=message)

    def send_and_save_video(self, update: Update, context: CallbackContext, vide_url: str, caption: str,
                            command: str):
        chat_id = update.message.chat_id
        query = self.get_command_parameter(command=command, update=update)

        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_VIDEO)
        new_url = self.downsize_dash_link(vide_url, maximum_size=360)
        try:
            message = context.bot.send_video(chat_id=chat_id, video=new_url,
                                             caption=caption, supports_streaming=True)
            self.save_media(update=update, command=command, type="video", query=query, message=message)

        except Exception as err:
            update.message.reply_text("Irgendwos hot do ned highaut ☹️")
