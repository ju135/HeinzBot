#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import logging
import os
import random
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, \
    Dispatcher

from utils.api_key_reader import read_key
from modules.job_register_bot import register_methods_in_file

mutedAccounts = list()


def load_modules(dp):
    modules = os.listdir(os.path.dirname("modules/"))
    modules = list(filter(lambda x: x[-3:] == ".py", modules))
    for module in modules:
        load_module(module, dp)


def load_module(name, dp: Dispatcher):
    # [:-3] in order to remove the .py ending
    name = name[:-3]
    path = "modules." + name
    imported = __import__(name=path)
    module = getattr(imported, name)

    # Load all classes inside a module
    classes = inspect.getmembers(module, inspect.isclass)
    clazz_name = None

    # pick the class that is inside the module and not imported
    for (name, clazz) in classes:
        if clazz.__module__ == path:
            clazz_name = name
            break
    if clazz_name is None:
        return

        # create class instance
    clazz = getattr(module, clazz_name)
    if hasattr(clazz, "_active"):
        if clazz._active is not True:
            return
    else:
        return

    inst = clazz()
    methods = inspect.getmembers(inst, predicate=inspect.ismethod)
    run_daily_methods = list(filter(lambda x: hasattr(x[1], "_daily_run_time_decorator") and
                                              hasattr(x[1], "_daily_run_name_decorator"), methods))
    if len(run_daily_methods) > 0:
        register_methods_in_file(run_daily_methods, dp)
    for (key, method) in methods:
        if hasattr(method, "_command") and hasattr(method, "_short_desc") and \
                hasattr(method, "_long_desc") and hasattr(method, "_usage"):
            register_command_handler(dp, method, inst)
        if hasattr(method, "_filter"):
            register_message_watcher(dp, method, inst)


def register_command_handler(dp: Dispatcher, method, inst):
    dp.add_handler(CommandHandler(method._command, method), group=1)
    help_text_func = getattr(inst, "add_help_text")
    help_text_func(method._command, method._short_desc, method._long_desc, method._usage)


def register_message_watcher(dp: Dispatcher, method, inst):
    dp.add_handler(MessageHandler(Filters.command, method), group=0)


def main():
    updater = Updater(read_key("telegram"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('who', who_is_muted))
    dp.add_handler(CommandHandler('allow', allow))

    load_modules(dp)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dp.add_handler(inline_caps_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater.start_polling()


def allow(bot, update):
    if update.message.from_user.username == "jajules":
        person = update.message.text.replace('/allow ', '')
        bot.send_message(chat_id=update.message.chat_id,
                         text=(person + ' deaf jetzt wieder mit mir reden.'))
        mutedAccounts.remove(person)
    else:
        update.message.reply_text('Sry du deafst des ned.. :(')


def who_is_muted(bot, update):
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


if __name__ == '__main__':
    main()
