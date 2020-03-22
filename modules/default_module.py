import json
import urllib

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Dispatcher

from sending_actions import send_photo_action
from utils.decorators import register_command, register_module


@register_module(active=True)
class DefaultModule:
    mutedAccounts = list()
    __commandList = ""
    keyFileName = "api-keys.json"

    def add_help_text(self, text):
        DefaultModule.__commandList += text

    @register_command(command="help", text="/help Show this help message. \n")
    def help(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id(update)
        context.bot.send_message(chat_id=chat_id, text=self.__commandList)

    def get_chat_id(self, update: Update):
        return update.message.chat_id

    # In Version 12 of the telegram bot some major changes were made.
    @register_command(command="default", text="/default Show a default message. \n")
    def default_command(self, update: Update, context: CallbackContext):
        # Get the new job handler
        job = context.job

        # Get the chat id to reply to
        chat_id = self.get_chat_id(update)

        # Send a message
        context.bot.send_message(chat_id=chat_id, text="Default command")

        # Send an animation
        animation_url = "https://media.giphy.com/media/gw3IWyGkC0rsazTi/source.gif"
        context.bot.send_animation(chat_id=chat_id, animation=animation_url)

        # Send a sticker
        # Sticker need to have an ID or a file or a URL path
        file_url = "https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.webp"

        # Download the file
        # sticker = urllib.request.urlopen(url=file_url)

        # Or open it
        # sticker = open(file_url, "rb")
        context.bot.send_sticker(chat_id=chat_id, sticker=file_url)

    def get_api_key(self, key_name):
        f = open(self.keyFileName, "r")
        key_data = json.load(f)
        try:
            data = key_data[key_name]
            return data
        except:
            print(key_name + " not found")
            return ""

    @register_command(command="mute", text="/mute $user Mute a user")
    def mute(self, update: Update, context: CallbackContext):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/mute ', '')

            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=(person + ' wird gemutet!'))
            self.mutedAccounts.append(person)
        else:
            update.message.reply_text('Sry du deafst kan muten..')

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
