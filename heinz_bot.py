import inspect
import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, Dispatcher, \
    CallbackQueryHandler

from modules.job_register_bot import register_methods_in_file, send_awake_to_subscriber
from utils.api_key_reader import read_key


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
            register_message_watcher(dp, method)
        if hasattr(method, "_isInline"):
            register_message_watcher(dp, method)
        if hasattr(method, "_forCommand"):
            register_callback_query(dp, method)


def register_command_handler(dp: Dispatcher, method, inst):
    dp.add_handler(CommandHandler(method._command, method), group=1)
    help_text_func = getattr(inst, "add_help_text")
    help_text_func(method._command, method._short_desc, method._long_desc, method._usage)


def register_message_watcher(dp: Dispatcher, method):
    dp.add_handler(MessageHandler(Filters.command, method), group=0)


def register_inline_cap(dp: Dispatcher, method):
    dp.add_handler(InlineQueryHandler(method), group=0)


def register_callback_query(dp: Dispatcher, method):
    if method._isMaster:
        dp.add_handler(CallbackQueryHandler(method), group=2)
    else:
        dp.add_handler(CallbackQueryHandler(method, pattern=method._forCommand), group=3)


def main():
    updater = Updater(read_key("telegram"), use_context=True)
    dp = updater.dispatcher
    load_modules(dp)
    send_awake_to_subscriber(dp)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater.start_polling()


if __name__ == '__main__':
    main()
