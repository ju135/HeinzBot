#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import random
import inspect

from telegram import ChatAction, InlineQueryResultArticle, InputTextMessageContent, Sticker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from CalenderRead import send_first_appointment_of_day, setup_day_ended
from RandomText import get_random_ask_answer, get_random_quote_text, get_random_free_text
from GoogleSearch import get_image, get_gif, get_youtube
from SendingActions import send_photo_action, send_video_action
from InspireBot import receive_quote, send_quote_with_text
from Rule34Bot import fetch_porn
from OENachrichtenBot import get_newest_news
from APIKeyReader import read_key
from CatBot import receive_cat
from MemeBot import receive_meme
from CalenderRead import send_day_ended_sticker
from RedditBot import send_funny_submission, send_subreddit_submission
from CommicBot import receive_comic, send_comic_if_new
from MittagBot import receive_menue
from Modules.LetMeGoogleBot import create_google_request

import requests
import logging

mutedAccounts = list()
configFile = "config.json"
modules = []


def has_rights(update):
    if update.message.from_user.name in mutedAccounts:
        update.message.reply_text(
            '..hot wer wos gsogt?')
        return False
    if update.message.from_user.last_name in mutedAccounts:
        update.message.reply_text(
            '..hot wer wos gsogt?')
        return False
    return True


@send_photo_action
def image(bot, update):
    if not (has_rights(update)):
        return
    get_image(bot, update)


@send_photo_action
def yt(bot, update):
    if not (has_rights(update)):
        return
    get_youtube(bot, update)


@send_video_action
def gif(bot, update):
    if not (has_rights(update)):
        return
    get_gif(bot, update)


@send_video_action
def cat(bot, update):
    if not (has_rights(update)):
        return
    receive_cat(bot, update)


@send_photo_action
def rule34(bot, update):
    if not (has_rights(update)):
        return
    fetch_porn(bot, update)


# LetMeGoogleThatBot
def google(bot, update):
    if not (has_rights(update)):
        return
    create_google_request(bot, update)


@send_photo_action
def meme(bot, update):
    if not (has_rights(update)):
        return
    receive_meme(bot, update)


@send_photo_action
def quote(bot, update):
    if not (has_rights(update)):
        return
    receive_quote(bot, update)


def funny(bot, update):
    if not (has_rights(update)):
        return
    send_funny_submission(bot, update)


def reddit(bot, update):
    if not (has_rights(update)):
        return
    send_subreddit_submission(bot, update)


def get_news(bot, update):
    if not (has_rights(update)):
        return
    get_newest_news(bot, update)


def food(bot, update):
    if not (has_rights(update)):
        return
    receive_menue(bot, update)


def unknown(but, update):
    if not (has_rights(update)):
        return
    update.message.reply_text("Ich nix verstehen... 😢")


def bop(bot, update):
    if not (has_rights(update)):
        return
    chat_id = update.message.chat_id
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']

    bot.send_photo(chat_id=chat_id, photo=url)


def comic(bot, update):
    if not (has_rights(update)):
        return
    receive_comic(bot, update)


def ask(bot, update):
    if not (has_rights(update)):
        return
    if '?' not in update.message.text:
        update.message.reply_text("des woa jetzt aber ka frog..")
        return
    update.message.reply_text(get_random_ask_answer())


def daily_appointment(bot, job):
    appointment = send_first_appointment_of_day()

    if appointment:
        bot.send_message(chat_id=job.context, text=appointment)
        setup_day_ended(job)
    else:
        # send day is ended, if its a week day without appointment
        d = datetime.datetime.now()
        if d.isoweekday() in range(1, 6):
            bot.send_message(chat_id=job.context,
                             text=get_random_free_text())
            send_day_ended_sticker(bot, job)


def daily_quote(bot, job):
    # send quote of the day
    send_quote_with_text(bot, job, get_random_quote_text())


def daily_comic(bot, job):
    send_comic_if_new(bot, job)


def daily_timer(bot, update, job_queue):
    if job_queue.get_jobs_by_name("Daily_Quote"):
        bot.send_message(chat_id=update.message.chat_id,
                         text='Da bot laft eh scho.')
        return
    bot.send_message(chat_id=update.message.chat_id,
                     text='Jawohl Chef, bot is augstart!')

    time_morning = datetime.time(8, 15, 0, 0)
    job_queue.run_daily(daily_appointment, time_morning, days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id,
                        name="Daily_Appointment")
    time_ten = datetime.time(10, 0, 0, 0)
    job_queue.run_daily(daily_quote, time_ten, days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id,
                        name="Daily_Quote")
    time_twelve = datetime.time(hour=12, minute=00, second=0)
    job_queue.run_daily(daily_comic, time_twelve, days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id,
                        name="Daily_Comic")


def read_config():
    f = open(configFile, "r")
    modules = json.load(f)
    for module in modules:
        data = modules[module]
        if data["enabled"]:
            modules[data["command"]] = True
            load_module(module)


def load_module(name):
    path = "Modules." + name
    module = __import__(name=path)

    pass


def main():
    updater = Updater(read_key("telegram"))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('ask', ask))
    dp.add_handler(CommandHandler('image', image))
    dp.add_handler(CommandHandler('gif', gif))
    dp.add_handler(CommandHandler('yt', yt))
    dp.add_handler(CommandHandler('mute', mute))
    dp.add_handler(CommandHandler('who', who_is_muted))
    dp.add_handler(CommandHandler('cat', cat))
    dp.add_handler(CommandHandler('rule34', rule34))
    dp.add_handler(CommandHandler('allow', allow))
    dp.add_handler(CommandHandler('news', get_news))
    dp.add_handler(CommandHandler('reverse', reverse))
    dp.add_handler(CommandHandler('quote', quote))
    dp.add_handler(CommandHandler('meme', meme))
    dp.add_handler(CommandHandler('funny', funny))
    dp.add_handler(CommandHandler('reddit', reddit))
    dp.add_handler(CommandHandler('comic', comic))
    dp.add_handler(CommandHandler('moizeit', food))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('google', google))
    dp.add_handler(CommandHandler('ya', google))
    dp.add_handler(CommandHandler('ddg', google))

    #read_config()

    daily_handler = CommandHandler('start', daily_timer, pass_job_queue=True)
    dp.add_handler(daily_handler)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    dp.add_handler(inline_caps_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dp.add_handler(unknown_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater.start_polling()
    # updater.idle()


def allow(bot, update):
    if update.message.from_user.username == "jajules":
        person = update.message.text.replace('/allow ', '')
        bot.send_message(chat_id=update.message.chat_id,
                         text=(person + ' deaf jetzt wieder mit mir reden.'))
        mutedAccounts.remove(person)
    else:
        update.message.reply_text('Sry du deafst des ned.. :(')


def who_is_muted(bot, update):
    if not (has_rights(update)):
        return
    text = "Sprechverbot: \n"
    for i in mutedAccounts:
        text += "- " + i + "\n"
    bot.send_message(chat_id=update.message.chat_id,
                     text=text)


def mute(bot, update):
    if update.message.from_user.username == "jajules":
        person = update.message.text.replace('/mute ', '')
        bot.send_message(chat_id=update.message.chat_id,
                         text=(person + ' wird gemutet!'))
        mutedAccounts.append(person)
    else:
        update.message.reply_text('Sry du deafst kan muten..')


def reverse(bot, update):
    if not (has_rights(update)):
        return
    t = get_command_parameter("/reverse", update)
    if t:
        bot.send_message(chat_id=update.message.chat_id, text=t[::-1])


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    text = ""
    for s in query:
        r = random.randint(0, 100)
        if r > 50:
            text += s.upper()
        else:
            text += s.lower()

    results = list()
    results.append(
        InlineQueryResultArticle(
            id=text,
            title='Go Funky',
            input_message_content=InputTextMessageContent(text),
            thumb_url='https://imgflip.com/s/meme/Mocking-Spongebob.jpg',
            description="Vorschau: \"" + text + "\""
            # "Schreib irgendan spöttischen Text.\nA bissal spotten hot no kan gschodt."
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command + " "):
        return text[len(command) + 1:]
    if text.startswith(command + b + " "):
        return text[len(command + b) + 1:]


def get_random_string(l: [str]) -> str:
    return l[random.randint(0, len(l) - 1)]


def help(bot, update):
    commandlist = """/image - Googlet noch an foto und schickts 👌🏼
/gif - Googlet noch an gif und schickts 👌🏼
/yt - Schickt as erste youtube video wos findt. 
/reverse - reversiert den übergebenen Text.
/ask - Entscheidungshilfe bei ja/nein fragen.
/rule34 - Schickt a Rule34 Bild zu gegebene Begriffe.
/news - Schickt a gegebene Anzahl an OÖ News. 
/quote - Schickt a Bild mit an inspirierenden Spruch.. ✍🏼
/cat - Schickt a katzal-gif mit an Text drüber. 🐈
/meme - Schickt a random meme. 🧙‍♂️
/reddit - Wennsd an subreddit angibst schick i da ans vo die top 30 hot bilder oder videos. 😎 als 2. parameter kanns an index angeben.
/funny - i schick da funny reddit submissions. 👌
/comic - do schick i da an comic. 😉
/moizeit - Wos heid in Hagenberg zum fuadan gibt
/google - Wenn wieder mol wer zfaul zum Googlen is..  😌
/ddg - I suach für die auf DuckDuckGo.
/ya - Let me yahoo that for you.
/start - Bot starten (Täglicher Vorlesungs-Reminder)"""
    if not (has_rights(update)):
        return
    update.message.reply_text(commandlist)


if __name__ == '__main__':
    main()
