import base64
import datetime
import json
import os
import random
from datetime import date, timedelta

import requests
from gtts import gTTS
from gtts.lang import tts_langs
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, run_daily, send_action

HEINZ_SAY_MP_ = "heinzSay.mp3"


@register_module()
class ComicBot(AbstractModule):
    @register_command(command="say", short_desc="Says the things you want him to say.",
                      long_desc="Says the things you want him to say by setting a language and a text.",
                      usage=["/say [lang] [text]", "/say de Random Text"])
    @send_action(action=ChatAction.RECORD_AUDIO)
    def say(self, update: Update, context: CallbackContext):

        chat_id = update.message.chat_id

        text = self.get_command_parameter("/say", update)

        splitted = text.split(" ", 1)
        if len(splitted) == 2 and len(splitted[0]) == 2:
            fn = self.makeBase64Filename(text)

            # Language in which you want to convert
            language = splitted[0]
            langs = tts_langs("com")
            if language.lower() not in langs:
                update.message.reply_text("I versteh die sproch ned!")
            else:
                words = gTTS(text=splitted[1], lang=language, slow=False)
                words.save(fn)
                audio = open(fn, 'rb')
                context.bot.send_audio(chat_id=chat_id, audio=audio, caption="Sogs ma noch!")
                try:
                    os.remove(fn)
                except:
                    print("No file deleted")
        else:
            update.message.reply_text("Oida selbst i versteh die ned!")

    def makeBase64Filename(self, text):
        message_bytes = text.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
