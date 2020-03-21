import requests
from google_search import get_command_parameter, percent_encoding


def receive_cat(bot, update):
    query = get_command_parameter("/cat", update)
    chat_id = update.message.chat_id
    if not query:
        img = 'https://cataas.com/c/gif'
    else:
        query = percent_encoding(query)
        img = 'https://cataas.com/c/gif/s/' + query

    bot.send_animation(chat_id=chat_id, animation=img)
