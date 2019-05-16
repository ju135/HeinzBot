from ics import Calendar
import datetime
from APIKeyReader import read_key
from urllib.request import urlopen   # py3


def send_first_appointment_of_day():
    sorted_events = get_current_day_events()
    if sorted_events:
        text = "Guatn Moang!\n"
        text += "Heit is \"" + sorted_events[0].name
        text += "\" um " + str(sorted_events[0].begin.datetime.hour) + ":" + str(sorted_events[0].begin.datetime.minute) \
                + "Uhr im \"" + sorted_events[0].location + "\"!\nBG HB"
        return text


def setup_day_ended(job_queue, update):
    sorted_events = get_current_day_events()
    if not sorted_events:
        return
    last_event = sorted_events.pop()
    time = last_event.end.datetime
    #current_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
    job_queue.run_once(send_day_ended_sticker, time, context=update.message.chat_id)


def send_day_ended_sticker(bot, job):
    chat_id = job.context
    sticker = "CAADBAADfQADgU2cAAGz-YOa3nevdgI"
    bot.sendSticker(chat_id, sticker)


def get_current_day_events():
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
