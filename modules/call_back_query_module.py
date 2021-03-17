from telegram import Update
from telegram.ext import CallbackContext, DispatcherHandlerStop
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_callback_query_handler


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

        update.callback_query.message.reply_text("Herst Lorent, hab i mid dia gredt?")
