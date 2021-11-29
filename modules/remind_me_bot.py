from telegram import Update, Message
from telegram.ext import CallbackContext
import datetime

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors
from utils.random_text import get_random_string_of_messages_file


def command(context: CallbackContext):
    message: Message = context.job.context  # The message object is stored as job data
    message.reply_text(get_random_string_of_messages_file("constants/messages/reminder_messages.json"))


@register_module()
class RemindMeBot(AbstractModule):
    @register_command(command="remindme",
                      short_desc="Reminds you of important stuff",
                      long_desc=f"Add a long description here.."
                                f"...",
                      usage=["/remindme $time", "/remindme 2h", "/remindme 30min"])
    @log_errors()
    def remind_me_command(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/remindme", update)

        #if not query:
        #    update.message.reply_text("Jetzt glei oda wos? Sunst miassast ma a Zeit augem.")
        #    return

        time_change = datetime.timedelta(seconds=30, hours=-1) # Hours -1 to respect the timezone
        trigger_time = datetime.datetime.now() + time_change
        #update.message
        context.dispatcher.job_queue.run_once(callback=command, when=trigger_time, context=update.message)


