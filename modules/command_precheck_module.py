from telegram import Update
from telegram.ext import CallbackContext, Filters, DispatcherHandlerStop
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_message_watcher


@register_module()
class CommandPrechecks(AbstractModule):

    @register_message_watcher(filter=Filters.command)
    def run_prechecks(self, update: Update, context: CallbackContext):
        self.has_rights(update, context)
        self.unknown(update, context)

    def has_rights(self, update: Update, context: CallbackContext):
        if update.message.from_user.name in AbstractModule.mutedAccounts:
            update.message.reply_text('..hot wer wos gsogt?')
            raise DispatcherHandlerStop()
        if update.message.from_user.last_name in AbstractModule.mutedAccounts:
            update.message.reply_text('..hot wer wos gsogt?')
            raise DispatcherHandlerStop()

    def unknown(self, update: Update, context: CallbackContext):
        group = 1  # CommandHandler Queue
        handlers = context.dispatcher.handlers

        for handler in handlers[group]:
            check = handler.check_update(update)
            if check is not None and check is not False:
                return
        update.message.reply_text("Ich nix verstehen... 😢")
