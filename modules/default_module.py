import json
import urllib
from smtpd import usage

import requests
import telegram
from telegram import Update, MessageEntity, ChatAction
from telegram.ext import CommandHandler, CallbackContext, Dispatcher, Filters, DispatcherHandlerStop

from modules.abstract_module import AbstractModule
from utils.decorators import register_command, register_module, register_message_watcher, send_action, \
    register_callback_query_handler
from utils.random_text import get_random_string_of_messages_file


@register_module()
class DefaultModule(AbstractModule):

    @register_command(command="help", short_desc="Show this help message.", long_desc="", usage=[""])
    def help(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id(update)
        cmd_list = sorted(AbstractModule._commandList, key=lambda x: x["command"])
        parameter = self.get_command_parameter("/help", update)
        if parameter is not None:
            parameters = parameter.split(" ")
            help_command = parameters[0].replace("/", "")
            for cmd_desc in cmd_list:
                if help_command == cmd_desc["command"]:
                    context.bot.send_message(chat_id=chat_id,
                                             text=self.__format_detailed_command_description(cmd_desc),
                                             parse_mode=telegram.ParseMode.MARKDOWN)
                    return
            context.bot.send_message(chat_id=chat_id, text=f"Kommando `{help_command}` existiert nicht.",
                                     parse_mode=telegram.ParseMode.MARKDOWN)
            return

        message = "*Commands*\n" \
                  "_For more detailed descriptions write:_ `/help $command`\n\n"

        # longest_cmd_length = max(list(map(lambda x: len(x["command"]), cmd_list)))
        for cmd_desc in cmd_list:
            message += f"/{cmd_desc['command']} - {cmd_desc['short_desc']}\n"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    def __format_detailed_command_description(self, command_description) -> str:
        command = command_description["command"]
        long_des = command_description["long_desc"]
        usages = command_description["usage"]

        message = f"*{command}*\n" \
                  f"{long_des}\n\n" \
                  f"_Verwendung_:\n"

        message += "`"
        for usage in usages:
            message += f"{usage}\n"
        message += "`"

        return message

    # In Version 12 of the telegram bot some major changes were made.
    @register_command(command="default", short_desc="Show a default message.", long_desc="", usage=[""])
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

    @register_command(command="mute", short_desc="Mute a user", long_desc="", usage=[""])
    def mute(self, update: Update, context: CallbackContext):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/mute ', '')

            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=(person + ' wird gemutet!'))
            self.mutedAccounts.append(person)
        else:
            update.message.reply_text('Sry du deafst kan muten..')

    @register_command(command="bop", short_desc="Cute doggo bilder 🐕", long_desc="", usage=[""])
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    def bop(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        context.bot.send_photo(chat_id=chat_id, photo=url)

    @register_command(command="ask", short_desc="Entscheidungshilfe bei ja/nein fragen.", long_desc="", usage=[""])
    def ask(self, update: Update, context: CallbackContext):
        if '?' not in update.message.text:
            update.message.reply_text("des woa jetzt aber ka frog..")
            return
        update.message.reply_text(get_random_string_of_messages_file("constants/messages/ask_answers.json"))

    @register_command(command="reverse", short_desc="Reversiert den übergebenen Text.", long_desc="", usage=[""])
    def reverse(self, update: Update, context: CallbackContext):
        t = self.get_command_parameter("/reverse", update)
        if t:
            context.bot.send_message(chat_id=update.message.chat_id, text=t[::-1])

    @register_command(command="allow", short_desc="allows a user", long_desc="", usage=["/allow $user"])
    def allow(self, update: Update, context: CallbackContext):
        if update.message.from_user.username == "jajules":
            person = update.message.text.replace('/allow ', '')
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=(person + ' deaf jetzt wieder mit mir reden.'))
            AbstractModule.mutedAccounts.remove(person)
        else:
            update.message.reply_text('Sry du deafst des ned.. :(')

    @register_command(command="who", short_desc="Shows who is muted", long_desc="", usage=[""])
    def who_is_muted(self, update: Update, context: CallbackContext):
        text = "Sprechverbot: \n"
        for i in AbstractModule.mutedAccounts:
            text += "- " + i + "\n"
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=text)
