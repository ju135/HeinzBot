import logging
import googletrans
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action


@register_module()
class TranslateBot(AbstractModule):
    @register_command(command="trans", short_desc="Translates the given sentence.",
                      long_desc="Translates the given sentence and returns the translation by setting a base language, translation language and providing a text.",
                      usage=["/trans [lang-base] [lang-trans] [text]", "/trans en de Please translate this to German."])
    @send_action(action=ChatAction.TYPING)
    def translate(self, update: Update, context: CallbackContext):
        try:
            self.log(text="Trying to translate something..", logging_type=logging.DEBUG)

            chat_id = update.message.chat_id
            text = self.get_command_parameter("/trans", update)

            if text is not None:
                splitted = text.split(" ", 2)

                langs = googletrans.LANGCODES.values()
                if len(splitted) == 3 and len(splitted[0]) == 2 and splitted[0] in langs and len(splitted[1]) == 2 and splitted[1] in langs:
                    langfrom = splitted[0]
                    langto = splitted[1]
                else:
                    langfrom = ""
                    langto = "de"
                    splitted = text.split(" ", 1)

                translator = googletrans.Translator()
                if (langfrom and langto):
                    transtext = translator.translate(text=splitted[2], src=langfrom, dest=langto)
                    context.bot.send_message(chat_id=chat_id, text="Übersetzt von " + googletrans.LANGUAGES.get(langfrom).capitalize() + " zu " + googletrans.LANGUAGES.get(langto).capitalize() + " hast des:\n" + transtext.text)
                else:
                    transtext = translator.detect(splitted[1])
                    if transtext.confidence > 0.4:
                        langfrom = transtext.lang
                        transtext = translator.translate(text=splitted[1], src=transtext.lang, dest=langto)
                        context.bot.send_message(chat_id=chat_id, text="Übersetzt von " + googletrans.LANGUAGES.get(langfrom).capitalize() + " zu " + googletrans.LANGUAGES.get(langto).capitalize() + " hast des:\n" + transtext.text)
                    else:
                        context.bot.send_message(chat_id=chat_id, text="Oida, i bin ma echt ned sicha wos des Gspeibad hasn soi.. Probiers nuamoi und gib ma vielleicht de Ausgaungssproch mit au!")

            else:
                update.message.reply_text("I moa du host do wos vagessn Kollege!")
        except Exception as err:
            #self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")