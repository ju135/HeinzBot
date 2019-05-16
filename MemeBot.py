import requests
import json
import requests

# random not working
def receive_meme(bot, update):
    chat_id = update.message.chat_id
    url = 'https://api.memeload.us/v1/random'
    r = requests.get(url)
    meme_data = json.loads(r.text)
    bot.send_photo(chat_id=chat_id, photo=meme_data["image"], caption=meme_data["title"])
