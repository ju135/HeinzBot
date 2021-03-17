import logging
import telegram
import json
import re
from telegram import Update, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from repository.database import Database
from utils.decorators import register_module, register_command, send_action, log_errors, \
    register_callback_query_handler, members_only


@register_module()
class DatabaseBot(AbstractModule):
    @register_command(command="db", short_desc="Do something with the database.",
                      long_desc="Lets you delete, get things from the database e.g for a clean chat without nude pics ;).",
                      usage=["/db [g](get),[d](delete) [command]", "/db d husky"])
    @members_only()
    @log_errors()
    def database(self, update: Update, context: CallbackContext):
        self.log(text="Trying to delete entries and pictures", logging_type=logging.INFO)
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/db", update)

        if text is not None:
            split = text.split(" ", 1)
            if len(split) < 2:
                context.bot.send_message(chat_id=chat_id, text="Kollege an suchtext musst schau augeben!",
                                         parse_mode=telegram.ParseMode.MARKDOWN)
                return
            if split[0] == "d":  #
                keyboard = [
                    [InlineKeyboardButton("Yes",
                                          callback_data=json.dumps({"answer": "database:yes", "data": split[1]})),
                     InlineKeyboardButton("No", callback_data=json.dumps({"answer": "database:no"})),
                     ]
                ]
                markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Wüst wirklich olles löschn?", reply_markup=markup)

            if split[0] == "g":
                results = self.get_data(chat_id=chat_id, searchtext=split[1])
                if len(results) == 0:
                    context.bot.send_message(chat_id=chat_id, text="Olles schau glöscht!",
                                             parse_mode=telegram.ParseMode.MARKDOWN)
                    return
                context.bot.send_message(chat_id=chat_id, text=results, parse_mode=telegram.ParseMode.MARKDOWN)

    def get_data(self, chat_id, searchtext: str):
        return Database.instance().get_from_media_by_command(chat_id=chat_id, searchtext=searchtext)

    @register_callback_query_handler(command=re.compile(".*(database).*"))
    def database_remove_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        chat_id = query.message.chat_id
        callback = json.loads(query.data)

        if callback['answer'] == "database:yes":
            results = self.get_data(chat_id=chat_id, searchtext=callback['data'])
            for image in results:
                try:
                    query.bot.delete_message(chat_id=chat_id, message_id=image['message_id'])
                except Exception as err:
                    self.log(text="No danger! Image just not found for deletion", logging_type=logging.INFO)

            Database.instance().delete_from_media_by_command(chat_id=chat_id, searchtext=callback['data'])
            query.edit_message_text(text="Ois glöscht Kollege wir san wieder sauber!")

        else:
            query.edit_message_text(text="Guad daun los mas!")
