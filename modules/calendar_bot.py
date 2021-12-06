import requests
import bs4
import datetime
import dateparser

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
                      usage=["/open"])
    @log_errors()
    def remind_me_command(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        self.run_command(chat_id, context)

    @run_daily(name="daily_calendar", time=datetime.time(hour=9 - 1, minute=0, second=0))
    def send_comic_if_new(self, context: CallbackContext, chat_id: str):
        # No daily message when not in the kb-chat
        kb_chat_id = read_key("kb_chat_id")
        if chat_id != kb_chat_id:
            return
        self.run_command(chat_id, context)

    def run_command(self, chat_id: str, context):
        # only allow this command in the kb-chat
        kb_chat_id = read_key("kb_chat_id")
        if chat_id != kb_chat_id:
            context.bot.send_message(chat_id=chat_id, text="Sorry, this command is only working in the maintainers chat.")
            return
        calendar_secret = read_key("calendar_secret")
        date_to_retrieve = dateparser.parse("02.12.2021", locales=["de-AT"], settings={'TIMEZONE': 'Europe/Vienna'})
        current_day_string1 = date_to_retrieve.strftime("%Y/%m/%d")  # Creates a string like "2021/12/05"
        current_day_string2 = date_to_retrieve.strftime("%Y%m%d")  # Creates a string like "20211205"
        url = f"https://{calendar_secret}/tz.php?std_time_offset=0&document_width=562&return={current_day_string1}"
        response = requests.get(url)
        bs_content = bs4.BeautifulSoup(response.content, 'html.parser')
        meta_url = bs_content.findAll("meta", {'property': 'og:url'})[0]['content']
        substring = meta_url.split(f"{calendar_secret}/")[1]
        new_url = f"https://{calendar_secret}/tz.php?std_time_offset=0&document_width=562&return={substring}"
        response2 = requests.get(new_url)

        block_before_content = response2.text.split("\"" + current_day_string2 + "\":{\"name\":")[1]
        content_description = block_before_content.split("\"")[1]
        link = block_before_content.split("\"video\":")[1].split("\"")[1].replace("\\", "")

        if link is None or link == "":
            context.bot.send_message(chat_id=chat_id, text="Unfortunately, no link could be found.")
            return

        caption = f"Heite im Kalender: {content_description}"
        context.bot.send_video(chat_id=chat_id, video=link, caption=caption, supports_streaming=True)