from modules.abstract_module import AbstractModule
from modules.default_module import DefaultModule
from google_search import get_command_parameter, percent_encoding
from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from sending_actions import send_action
from utils.decorators import register_command, register_module


@register_module()
class CatBot(AbstractModule):
    @register_command(command="cat", text="Sends cat")
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    def cat_command(self, update: Update, context: CallbackContext):
        query = get_command_parameter("/cat", update)
        chat_id = update.message.chat_id
        if not query:
            img = 'https://cataas.com/c/gif'
        else:
            query = percent_encoding(query)
            img = 'https://cataas.com/c/gif/s/' + query
        context.bot.send_animation(chat_id=chat_id, animation=img)