import datetime
import json

import bs4
import dateparser
import requests
from telegram import Update
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.api_key_reader import read_key
from utils.decorators import register_module, register_command, log_errors, run_daily


@register_module()
class CalendarBot(AbstractModule):
    @register_command(command="open",
                      short_desc="Opens the current door of the calendar",
                      long_desc=f"Opens the current door of the calendar, "
                                f"but only works in the chat-group of the maintainers.",
                      usage=["/open [other] [$date]", ["/open", "/open other",
                                                       "/open 01.12.2021", "/open other 01.12.2021"]])
    @log_errors()
    def open_calendar_command(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        query = self.get_command_parameter("/open", update)
        if query is None:
            self.run_command(chat_id, context)
            return

        choose_other_api = False
        if "other" in query:
            query = query.replace("other", "")
            choose_other_api = True

        date_to_retrieve = dateparser.parse(query, locales=["de-AT", "en-AT"],
                                            settings={'TIMEZONE': 'Europe/Vienna',
                                                      'PREFER_DAY_OF_MONTH': 'first',
                                                      'PREFER_DATES_FROM': 'future'})
        self.run_command(chat_id, context, date_to_retrieve, choose_other_api)

    @run_daily(name="daily_calendar_morning", time=datetime.time(hour=9 - 1, minute=0, second=0))
    def send_daily_calendar_morning(self, context: CallbackContext, chat_id: str):
        # No daily message when not in the kb-chat
        kb_chat_id = read_key("kb_chat_id")
        if chat_id != kb_chat_id:
            return
        self.run_command(chat_id, context)

    @run_daily(name="daily_calendar_afternoon", time=datetime.time(hour=14 - 1, minute=30, second=0))
    def send_daily_calendar_afternoon(self, context: CallbackContext, chat_id: str):
        # No daily message when not in the kb-chat
        kb_chat_id = read_key("kb_chat_id")
        if chat_id != kb_chat_id:
            return
        self.run_command(chat_id, context, other=True)

    def run_command(self, chat_id: str, context, date_to_retrieve=None, other=False):
        # only allow this command in the kb-chat
        kb_chat_id = read_key("kb_chat_id")
        if chat_id != kb_chat_id:
            context.bot.send_message(chat_id=chat_id,
                                     text="Sorry, this command is only working in the maintainers chat.")
            return
        if other:
            calendar_secret = read_key("calendar_secret2")
        else:
            calendar_secret = read_key("calendar_secret1")
        if date_to_retrieve is None:
            date_to_retrieve = datetime.datetime.now()

        if date_to_retrieve.month == 12:
            calendar_secret_december = read_key("calendar_secret_december")
            caption, video_url = _get_december_video_info(calendar_secret_december, date_to_retrieve)
        else:
            caption, video_url = _get_regular_video_info(calendar_secret, date_to_retrieve)

        if video_url is None or video_url == "":
            context.bot.send_message(chat_id=chat_id, text="Unfortunately, no link could be found.")
            return

        context.bot.send_video(chat_id=chat_id, video=video_url, caption=caption, supports_streaming=True)


def _get_regular_video_info(calendar_secret, date_to_retrieve) -> (str, str):
    current_day_string1 = date_to_retrieve.strftime("%Y/%m/%d")  # Creates a string like "2021/12/05"
    current_day_string2 = date_to_retrieve.strftime("%Y%m%d")  # Creates a string like "20211205"
    url = f"https://{calendar_secret}/tz.php?std_time_offset=0&document_width=562&return={current_day_string1}"
    response = requests.get(url)
    bs_content = bs4.BeautifulSoup(response.content, 'html.parser')
    search_string = "var datas = "
    script_with_url = next(filter(lambda x: search_string in x.text, bs_content.findAll("script"))).text
    # The script contains a json with the link which is stored in the javascript datas variable
    # Cut the front and back of the string to only be left with the json
    cut_in_front = script_with_url[script_with_url.find(search_string) + len(search_string):]
    json_end_delimiter = ";"
    json_string = cut_in_front[:cut_in_front.find(json_end_delimiter)]
    json_data = json.loads(json_string)
    today_data = json_data[current_day_string2]
    video_url = "https:" + today_data["video"]
    caption = "Des hob i heit im Kalender"
    if "name" in today_data:
        caption = f"Heite im Kalender: {today_data['name']}"
    return caption, video_url


def _get_december_video_info(calendar_secret: str, date_to_retrieve: datetime) -> (str, str):
    url = f"https://{calendar_secret}/day-{date_to_retrieve.day}"
    response = requests.get(url)
    bs_content = bs4.BeautifulSoup(response.content, 'html.parser')
    video_url = bs_content.find("video").attrs["lazy-src"]
    caption = "Heite im Kalender 🎅"
    return caption, video_url
