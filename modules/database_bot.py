import base64
import logging
import os

from gtts import gTTS
from gtts.lang import tts_langs, _main_langs
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors
from repository.database import Database


@register_module()
class DatabaseBot(AbstractModule):
    @register_command(command="database", short_desc="Do something with the database.",
                      long_desc="Lets you delete things from the database for a clean chat without nude pics ;).",
                      usage=["/database [command]", "/database husky"])
    @log_errors()
    @send_action(action=ChatAction.TYPING)
    def database(self, update: Update, context: CallbackContext):
        self.log(text="Trying to delete entries and pictures", logging_type=logging.INFO)
        self.get_data(update)

    def get_data(self, update: Update):
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/database", update)
        Database.instance().get_from_reddit_by_command(chat_id=chat_id, command=text)
