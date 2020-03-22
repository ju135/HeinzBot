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
class CallBackModule(AbstractModule):
    @register_callback_query_handler(command="master", master=True)
    def check_callbacks(self, update: Update, context: CallbackContext):
        group = 3  # CallBackQueryHandler Queue
        handlers = context.dispatcher.handlers

        for handler in handlers[group]:
            check = handler.check_update(update)
            if check is not None and check is not False:
                handler.handle_update(update, context.dispatcher, check, context)
                raise DispatcherHandlerStop()

        update.message.reply_text("Herst Lorent, hab i mid dia gredt?")
