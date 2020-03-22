from telegram import Update
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_command, register_module

base_url = "https://de.lmgtfy.com/"


@register_module()
class LetMeGoogleBot(AbstractModule):

    @register_command(command="google",
                      short_desc="Googles the term for you via the 'Let me google that for you API'", long_desc="", usage=[""])
    def google(self, update: Update, context: CallbackContext):
        self.create_google_request(update, context)

    @register_command(command="ya",
                      short_desc="Yahoos the term for you via the 'Let me google that for you API'", long_desc="", usage=[""])
    def yahoo(self, update: Update, context: CallbackContext):
        self.create_google_request(update, context)

    @register_command(command="ddg",
                      short_desc="DuckDuckGoes the term for you via the 'Let me google that for you API'", long_desc="", usage=[""])
    def duck_duck_go(self, update: Update, context: CallbackContext):
        self.create_google_request(update, context)

    def create_google_request(self, update: Update, context: CallbackContext):

        query1 = self.get_command_parameter("/google", update)
        query2 = self.get_command_parameter("/ya", update)
        query3 = self.get_command_parameter("/ddg", update)

        if query1 is not None:
            query1 = query1.replace(" ", "+")
            chat_id = update.message.chat_id
            context.bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query1)

        if query2 is not None:
            query2 = query2.replace(" ", "+")
            chat_id = update.message.chat_id
            context.bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query2 + "&s=y&t=w")

        if query3 is not None:
            query3 = query3.replace(" ", "+")
            chat_id = update.message.chat_id
            context.bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query3 + "&s=d&t=w")
