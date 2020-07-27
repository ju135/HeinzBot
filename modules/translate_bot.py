from googletrans import Translator
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
            #self.log(text="Trying to translate something..", logging_type=logging.DEBUG)

            chat_id = update.message.chat_id
            text = self.get_command_parameter("/trans", update)

            if text is not None:
                splitted = text.split(" ", 1)

                translator = Translator()
            else:
                update.message.reply_text("I moa du host do wos vagessn Kollege!")
        except Exception as err:
            #self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")
