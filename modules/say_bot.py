import base64
import logging
import os

from gtts import gTTS
from gtts.lang import tts_langs
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action

@register_module()
class SayBot(AbstractModule):
    @register_command(command="say", short_desc="Says the things you want him to say.",
                      long_desc="Says the things you want him to say by setting a language and a text.",
                      usage=["/say [lang] [text]", "/say de Random Text"])
    @send_action(action=ChatAction.RECORD_AUDIO)
    def say(self, update: Update, context: CallbackContext):
        try:
            self.log(text="Trying to say something", logging_type=logging.DEBUG)

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
                    except Exception as err:
                        self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            else:
                update.message.reply_text("Oida selbst i versteh die ned!")
        except Exception as err:
            self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")

    def makeBase64Filename(self, text):
        message_bytes = str.encode(text, encoding='ascii', errors='ignore')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message[0:10]
