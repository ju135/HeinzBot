from ics import Calendar
import datetime

from urllib.request import urlopen   # py3


def sendFirstAppointmentOfDay():
    url = "http://stundenplan.fh-ooe.at/ics/478e9a7c4017434979.ics"
    c = Calendar(urlopen(url).read().decode('utf-8'))
    e = c.events[0]
    current_time = datetime.datetime.now()

    filter_current_day = filter(
        lambda x: ((x.begin.datetime.day == current_time.day) & (x.begin.datetime.month == current_time.month)),
        c.events)
    filtered_day_list = list(filter_current_day)
    sorted_events = sorted(filtered_day_list, key=lambda x: x.begin.timestamp)
    if sorted_events:
        text = "Guatn Moang!\n"
        text += "Heit is \"" + sorted_events[0].name
        text += "\" um " + str(sorted_events[0].begin.datetime.hour) + ":" + str(sorted_events[0].begin.datetime.minute) \
                + "Uhr im \"" + sorted_events[0].location + "\"!\nBG HB"
        return text

