from ics import Calendar
import datetime
from datetime import datetime as d

from telegram.ext import CallbackContext

from utils.api_key_reader import read_key
from urllib.request import urlopen   # py3

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, run_daily
from utils.random_text import get_random_string_of_messages_file


@register_module()
class CalendarReadBot(AbstractModule):
    @run_daily(name="daily_appointment", time=datetime.time(hour=8 - 1, minute=30, second=0))
    def daily_appointment(self, context: CallbackContext, chat_id: str):
        appointment = _send_first_appointment_of_day()

        if appointment:
            context.bot.send_message(chat_id=chat_id, text=appointment)
            _setup_day_ended(context.job, chat_id)
        else:
            # send day is ended, if its a week day without appointment
            d = datetime.datetime.now()
            if d.isoweekday() in range(1, 6):
                context.bot.send_message(chat_id=chat_id,
                                 text=get_random_string_of_messages_file(
                                     "constants/messages/lecture_free_day_messages.json"))
                _send_day_ended_sticker(context.bot, context.job)


def _send_first_appointment_of_day():
    sorted_events = _get_current_day_events()
    if sorted_events:
        text = "Guatn Moang!\n"
        text += "Heit is \"" + sorted_events[0].name
        text += "\" um " + str(sorted_events[0].begin.datetime.hour) + ":" + str(sorted_events[0].begin.datetime.minute) \
                + "Uhr im \"" + sorted_events[0].location + "\"!\nBG HB"
        return text


def _setup_day_ended(job, chat_id):
    sorted_events = _get_current_day_events()
    if not sorted_events:
        return
    last_event = sorted_events.pop()
    time = d.fromtimestamp(last_event.end.timestamp+2)
    #current_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
    job.job_queue.run_once(_send_day_ended_sticker, time, context=chat_id)


def _send_day_ended_sticker(bot, job):
    chat_id = job.context
    sticker = "CAADBAADfQADgU2cAAGz-YOa3nevdgI"
    bot.sendSticker(chat_id, sticker)


def _get_current_day_events():
    url = read_key("ics-file-link")
    c = Calendar(urlopen(url).read().decode('utf-8'))
    current_time = datetime.datetime.now()
    lva_set = {"Lehrveranstaltung"}
    filter_current_day = filter(
        lambda x: ((x.begin.datetime.day == current_time.day) & (x.begin.datetime.month == current_time.month)
                   & (x.categories == lva_set)),
        c.events)
    filtered_day_list = list(filter_current_day)
    sorted_events = sorted(filtered_day_list, key=lambda x: x.begin.timestamp)
    return sorted_events
