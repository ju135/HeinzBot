import requests


def receive_quote(bot, update):
    r = requests.get('https://inspirobot.me/api?generate=true')
    chat_id = update.message.chat_id
    img = r.text
    bot.send_photo(chat_id=chat_id, photo=img)


def send_quote_with_text(bot, job, text):
    r = requests.get('https://inspirobot.me/api?generate=true')
    chat_id = job.context
    img = r.text
    bot.send_photo(chat_id=chat_id, photo=img, caption=text)
