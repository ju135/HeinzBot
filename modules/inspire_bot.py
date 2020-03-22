import datetime

import requests
from telegram import Update
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_command, run_daily, register_module
from utils.random_text import get_random_string_of_messages_file


@register_module()
class InspireBot(AbstractModule):

    @register_command(command="quote", text="Sends an inspiring picture with text")
    def receive_quote(self, update: Update, context: CallbackContext):
        r = requests.get('https://inspirobot.me/api?generate=true')
        chat_id = update.message.chat_id
        img = r.text
        context.bot.send_photo(chat_id=chat_id, photo=img)

    @run_daily(name="daily_quote", time=datetime.time(hour=11 - 1, minute=0, second=0))
    def send_quote_with_text(self, context: CallbackContext, chat_id: str):
        text = get_random_string_of_messages_file("constants/messages/quote_subtitles.json")
        r = requests.get('https://inspirobot.me/api?generate=true')
        img = r.text
        context.bot.send_photo(chat_id=chat_id, photo=img, caption=text)
