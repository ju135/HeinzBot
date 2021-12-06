import datetime
import dateparser
import pytz
import telegram
from telegram import Update, Message, User
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors
from utils.random_text import get_random_string_of_messages_file


def command(context: CallbackContext):
    message: Message = context.job.context[0]  # The message object is stored as job data
    specified_message = context.job.context[1]
    from_user: User = context.job.context[2]

    text = ""
    if from_user is not None:
        name = from_user.name
        name = from_user.full_name if name is None else name
        name = "Kollege" if name is None else name
        user_tag = f"[{name}](tg://user?id={from_user.id})\n"
        text += user_tag
    if specified_message is not None:
        text += f"🚨 {specified_message} 🚨"
    else:
        text += get_random_string_of_messages_file("constants/messages/reminder_messages.json")

    context.bot.send_message(chat_id=message.chat_id,
                             text=text,
                             reply_to_message_id=message.message_id,
                             parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)


@register_module()
class RemindMeBot(AbstractModule):
    @register_command(command="remindme",
                      short_desc="Reminds you of important stuff ⏰",
                      long_desc=f"Specify a time or time-interval together with an optional message  and "
                                f"I will remind you by replying to your command at the specified time.",
                      usage=["/remindme $time [$message]", "/remindme 2h", "/remindme 30min Time for coffee",
                             "/remindme 1h30min Drink some water", "/remindme 31.12.2021 New year"])
    @log_errors()
    def remind_me_command(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/remindme", update)

        if not query:
            update.message.reply_text("Jetzt glei oda wos? Sunst miassast ma a Zeit augem.")
            return

        query_parts = query.split(" ")
        date_part = query_parts[0]
        specified_message = None
        # Everything after the first space counts as message to be reminded of
        if len(query_parts) > 1:
            specified_message = " ".join(query_parts[1:])

        parsed_date = dateparser.parse(date_part, locales=["de-AT"], settings={'TIMEZONE': 'Europe/Vienna',
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

        message_to_reply = update.message
        user_to_tag = None
        if update.message.reply_to_message is not None:
            message_to_reply = update.message.reply_to_message
            if message_to_reply.from_user is not update.message.from_user:
                # tag the requesting user when replying to a different message
                user_to_tag = update.message.from_user

        update.message.reply_text(f"Passt, bitte oida - i möd mi dann zu dem Zeitpunkt: {formatted_date}")
        context.dispatcher.job_queue.run_once(callback=command,
                                              when=parsed_date,
                                              context=[message_to_reply, specified_message, user_to_tag])


