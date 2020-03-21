import requests
import random
import json
import datetime 
from datetime import date, timedelta


def receive_comic(bot, update):
    chat_id = update.message.chat_id
    current_comic_data = receive_current_comic_data()
    max_number = current_comic_data["num"]

    rand_index = random.randint(1, max_number)

    url = "https://xkcd.com/" + str(rand_index) + "/info.0.json"
    r = requests.get(url)
    rnd_comic = json.loads(r.text)
    bot.send_photo(chat_id=chat_id, photo=rnd_comic["img"], caption=rnd_comic["title"])


def send_comic_if_new(bot, job):
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
