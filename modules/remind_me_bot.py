import datetime
import dateparser
import pytz
from telegram import Update, Message
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors
from utils.random_text import get_random_string_of_messages_file


def command(context: CallbackContext):
    message: Message = context.job.context  # The message object is stored as job data
    message.reply_text(get_random_string_of_messages_file("constants/messages/reminder_messages.json"))


@register_module()
class RemindMeBot(AbstractModule):
    @register_command(command="remindme",
                      short_desc="Reminds you of important stuff ⏰",
                      long_desc=f"Specify a time or time-interval together with this command and I will "
                                f"remind you by replying to your initial message at the specified time.",
                      usage=["/remindme $time", "/remindme 2h", "/remindme 30min", "/remindme 31.12.2021"])
    @log_errors()
    def remind_me_command(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/remindme", update)

        if not query:
            update.message.reply_text("Jetzt glei oda wos? Sunst miassast ma a Zeit augem.")
            return

        parsed_date = dateparser.parse(query, settings={'TIMEZONE': 'Europe/Vienna',
                                                        'PREFER_DAY_OF_MONTH': 'first',
                                                        'PREFER_DATES_FROM': 'future'})
        if parsed_date is None:
            update.message.reply_text("I versteh de Zeitangabe leider ned.. Bitte formuliers a bissl ondas.")
            return

        formatted_date = parsed_date.strftime("%d.%m.%Y, %H:%M:%S")
        if parsed_date < datetime.datetime.now():
            update.message.reply_text(f"Wüst mi pflanzen? Der Zeitpunkt ({formatted_date}) is jo scho vorbei.. "
                                      f"Do kau i kan Reminder mochn.")
            return

        parsed_date = pytz.timezone('Europe/Vienna').localize(parsed_date)  # Set the timezone
        update.message.reply_text(f"Passt, bitte oida - i möd mi dann zu dem Zeitpunkt: {formatted_date}")
        context.dispatcher.job_queue.run_once(callback=command, when=parsed_date, context=update.message)


