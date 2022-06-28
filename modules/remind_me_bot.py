import datetime
import dateparser
import pytz
import telegram
from telegram import Update, Message, User
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors
from utils.random_text import get_random_string_of_messages_file
from repository.database import Database


def remind_me_callback(context: CallbackContext):
    db_job_id = context.job.context
    remind_me_job = Database.instance().get_remind_me_job_by_id(db_job_id)
    chat_id = remind_me_job["chat_id"]
    message_id = remind_me_job["message_id"]
    user_id = remind_me_job["user_id"]
    username = remind_me_job["username"]
    specified_message = remind_me_job["specified_message"]

    text = ""
    if user_id is not None:
        name = "Kollege" if username is None else username
        user_tag = f"[{name}](tg://user?id={user_id})\n"
        text += user_tag
    if specified_message is not None:
        text += f"🚨 {specified_message} 🚨"
    else:
        text += get_random_string_of_messages_file("constants/messages/reminder_messages.json")

    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_to_message_id=message_id,
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
    # Message sent, delete the job from the database
    Database.instance().delete_remind_me_job_by_id(db_job_id)


# This function can be called to re-schedule all remind me jobs (e.g. after a reboot)
def schedule_remind_me_jobs_from_db(dispatcher):
    # Delete expired jobs
    Database.instance().delete_all_expired_remind_me_jobs()
    # Read upcoming jobs
    jobs = Database.instance().get_upcoming_remind_me_jobs()
    for job in jobs:
        # Time has to be re-localized as time-zone information is lost in DB
        trigger_time = pytz.timezone('Europe/Vienna').localize(job["trigger_time"])
        job_id = job["id"]
        dispatcher.job_queue.run_once(callback=remind_me_callback,
                                      when=trigger_time,
                                      context=job_id)


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

        parsed_date = dateparser.parse(date_part,
                                       locales=["de-AT", "en-AT"],
                                       settings={'TIMEZONE': 'Europe/Vienna',
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
        chat_id = message_to_reply.chat_id
        message_id = message_to_reply.message_id
        user_id = None
        username = None
        if user_to_tag is not None:
            user_id = user_to_tag.id
            username = user_to_tag.name
            username = user_to_tag.full_name if username is None else username
        db_job_id = Database.instance().insert_into_remind_me_jobs(chat_id, message_id, user_id, username,
                                                                   specified_message, parsed_date)

        context.dispatcher.job_queue.run_once(callback=remind_me_callback,
                                              when=parsed_date,
                                              context=db_job_id)
