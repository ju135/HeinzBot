import requests
import random
import json
import datetime 
from datetime import date, timedelta

from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.default_module import DefaultModule
from sending_actions import send_action
from utils.decorators import register_module, register_command, run_daily


@register_module(active=True)
class ComicBot(DefaultModule):
    @register_command(command="comic", text="TODO")
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    def receive_comic(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        current_comic_data = receive_current_comic_data()
        max_number = current_comic_data["num"]

        rand_index = random.randint(1, max_number)

        url = "https://xkcd.com/" + str(rand_index) + "/info.0.json"
        r = requests.get(url)
        rnd_comic = json.loads(r.text)
        context.bot.send_photo(chat_id=chat_id, photo=rnd_comic["img"], caption=rnd_comic["title"])

    @run_daily(name="daily_comic", time=datetime.time(hour=14-1, minute=29, second=10))
    def send_comic_if_new(self, context: CallbackContext, chat_id: str):
        chat_id = "-1001325436798"
        context.bot.send_message(chat_id, "hoi")
        comic_data = receive_current_comic_data()
        comic_release_date = datetime.date(int(comic_data["year"]), int(comic_data["month"]), int(comic_data["day"]))
        yesterday = date.today() - timedelta(days=1)
        if yesterday == comic_release_date:
            context.bot.send_photo(chat_id=chat_id, photo=comic_data["img"], caption=("Neuer Comic: " + comic_data["title"]))


def send_comic_if_new2(bot, job):
    chat_id = job.context
    comic_data = receive_current_comic_data()
    comic_release_date = datetime.date(int(comic_data["year"]), int(comic_data["month"]), int(comic_data["day"]))
    yesterday = date.today() - timedelta(days=1)
    if yesterday == comic_release_date:
        bot.send_photo(chat_id=chat_id, photo=comic_data["img"], caption=("Neuer Comic: " + comic_data["title"]))
    

def receive_current_comic_data():
    url = "https://xkcd.com/info.0.json"
    r = requests.get(url)
    comic_data = json.loads(r.text)
    return comic_data
