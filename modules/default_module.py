import json
import urllib

import requests
from telegram import Update, MessageEntity, ChatAction
from telegram.ext import CommandHandler, CallbackContext, Dispatcher, Filters, DispatcherHandlerStop

from modules.abstract_module import AbstractModule
from utils.decorators import register_command, register_module, register_message_watcher, send_action, \
    register_callback_query_handler
from utils.random_text import get_random_string_of_messages_file


@register_module()
class DefaultModule(AbstractModule):

    @register_command(command="help", text=" Show this help message. \n")
    def help(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id(update)
        context.bot.send_message(chat_id=chat_id, text=AbstractModule._commandList)

    # In Version 12 of the telegram bot some major changes were made.
    @register_command(command="default", text=" Show a default message. \n")
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

    @register_command(command="mute", text=" $user Mute a user")
    def mute(self, update: Update, context: CallbackContext):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/mute ', '')

            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=(person + ' wird gemutet!'))
            self.mutedAccounts.append(person)
        else:
            update.message.reply_text('Sry du deafst kan muten..')

    @register_command(command="bop", text="Cute doggo bilder 🐕")
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    def bop(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        context.bot.send_photo(chat_id=chat_id, photo=url)

    @register_command(command="ask", text="Entscheidungshilfe bei ja/nein fragen.")
    def ask(self, update: Update, context: CallbackContext):
        if '?' not in update.message.text:
            update.message.reply_text("des woa jetzt aber ka frog..")
            return
        update.message.reply_text(get_random_string_of_messages_file("constants/messages/ask_answers.json"))

    @register_command(command="reverse", text="Reversiert den übergebenen Text.")
    def reverse(self, update: Update, context: CallbackContext):
        t = self.get_command_parameter("/reverse", update)
        if t:
            context.bot.send_message(chat_id=update.message.chat_id, text=t[::-1])

    @register_command(command="allow", text=" $user. Reallows a user.")
    def allow(self, update: Update, context: CallbackContext):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/allow ', '')
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=(person + ' deaf jetzt wieder mit mir reden.'))
            AbstractModule.mutedAccounts.remove(person)
        else:
            update.message.reply_text('Sry du deafst des ned.. :(')

    @register_command(command="who", text=" Show how is muted")
    def who_is_muted(self, update: Update, context: CallbackContext):
        text = "Sprechverbot: \n"
        for i in AbstractModule.mutedAccounts:
            text += "- " + i + "\n"
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=text)
