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

            if text is not None:
                splitted = text.split(" ", 1)
                fn = self.makeBase64Filename(text)+".mp3"

                langs = tts_langs("com")
                language = "de"  # fallback to german
                # Language in which you want to convert
                if len(splitted) == 2 and len(splitted[0]) == 2 and splitted[0] in langs:
                    language = splitted[0]
                    voice_text = splitted[1]
                else:
                    voice_text = text

                words = gTTS(text=voice_text, lang=language, slow=False)
                words.save(fn)
                audio = open(fn, 'rb')
                context.bot.send_voice(chat_id=chat_id, voice=audio, reply_to_message_id=update.message.message_id)
                try:
                    os.remove(fn)
                except Exception as err:
                    self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            else:
                update.message.reply_text("Wos?")
        except Exception as err:
            self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")

    def makeBase64Filename(self, text):
        message_bytes = str.encode(text, encoding='ascii', errors='ignore')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message[0:10]
