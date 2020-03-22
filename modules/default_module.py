import json
import urllib

from telegram import Update, MessageEntity
from telegram.ext import CommandHandler, CallbackContext, Dispatcher, Filters, DispatcherHandlerStop

from modules.abstract_module import AbstractModule
from sending_actions import send_photo_action
from utils.decorators import register_command, register_module, register_message_watcher


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

    @register_message_watcher(filter=Filters.command)
    def has_rights(self, update: Update, context: CallbackContext):
        if update.message.from_user.name in AbstractModule.mutedAccounts:
            update.message.reply_text('..hot wer wos gsogt?')
            raise DispatcherHandlerStop()
        if update.message.from_user.last_name in AbstractModule.mutedAccounts:
            update.message.reply_text('..hot wer wos gsogt?')
            raise DispatcherHandlerStop()

    @register_message_watcher(filter=Filters.command)
    def unknown(self, update: Update, context: CallbackContext):
        group = 1  # CommandHandler Queue
        handlers = context.dispatcher.handlers

        for handler in handlers[group]:
            check = handler.check_update(update)
            if check is not None and check is not False:
                return
        update.message.reply_text("Ich nix verstehen... 😢")
