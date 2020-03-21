import json
from multiprocessing.reduction import register

import requests
import telegram
from telegram.ext import CommandHandler
from Modules.DefaultModule import DefaultModule

from APIKeyReader import read_key
from Utils.Decorators import register

base_url = "https://de.lmgtfy.com/"


class LetMeGoogleBot(DefaultModule):

    def add_command(self, dp):
        instance = LetMeGoogleBot()
        dp.add_handler(CommandHandler('google', instance.create_google_request))
        dp.add_handler(CommandHandler('ya', instance.create_google_request))
        dp.add_handler(CommandHandler('ddg', instance.create_google_request))
        return dp

    def add_to_command_list(self):
        DefaultModule.commandList += "/google $term Googles the term for you via the 'Let me google that for you API' \n"
        DefaultModule.commandList += "/ya $term Yahoos the term for you via the 'Let me google that for you API' \n"
        DefaultModule.commandList += "/ddg $term DuckDuckGoes the term for you via the 'Let me google that for you API' \n"

    @register(command="google",
              text="/google $term Googles the term for you via the 'Let me google that for you API' \n")
    @register(command="ya",
              text="/ya $term Yahoos the term for you via the 'Let me google that for you API' \n")
    def create_google_request(self, bot, update):
        if not self.has_rights(update):
            return

        query1 = self.get_command_parameter("/google", update)
        query2 = self.get_command_parameter("/ya", update)
        query3 = self.get_command_parameter("/ddg", update)

        if query1 is not None:
            query1 = query1.replace(" ", "+")
            chat_id = update.message.chat_id
            bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query1)

        if query2 is not None:
            query2 = query2.replace(" ", "+")
            chat_id = update.message.chat_id
            bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query2 + "&s=y&t=w")

        if query3 is not None:
            query3 = query3.replace(" ", "+")
            chat_id = update.message.chat_id
            bot.send_message(chat_id=chat_id, text=base_url + "?q=" + query3 + "&s=d&t=w")
