﻿import base64
import logging
from datetime import date

import schedule
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, register_scheduler


@register_module()
class LogBot(AbstractModule):
    @register_command(command="log", short_desc="Gives authorized users the possibility to download log files",
                      long_desc="Gives authorized users the possibility to download log files",
                      usage=["/log [date]", "/log 06-06-2020", "/log today"])
    @send_action(action=ChatAction.UPLOAD_DOCUMENT)
    def send_log(self, update: Update, context: CallbackContext):
        try:
            chat_id = update.message.chat_id
            text = self.get_command_parameter("/log", update)

            if "today" in text:
                today = date.today()
                today_log = today.strftime("%d-%m-%Y")
                text = today_log
            logfile = open("log/" + text + ".log", 'rb')
            if logfile.readable():
                context.bot.send_document(chat_id=chat_id, document=logfile, caption="Bitte schau wos foisch rennt :(")
            else:
                update.message.reply_text("Bitte gib a gscheids datum ein!")
        except Exception as err:
            self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Oida bitte möd di! Wia miasn iagnd wie zum Log kuma!")

    def clearLogs(self):
        print("cleared")

    @register_scheduler(name="log")
    def scheduled(self):
        schedule.every().minute.do(self.clearLogs)

    def makeBase64Filename(self, text):
        message_bytes = text.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
