import datetime
from functools import wraps
from telegram.ext import Filters


def register_command(command, short_desc, long_desc, usage):
    def register_wrapper(func):
        func._command = command
        func._short_desc = short_desc
        func._long_desc = long_desc
        func._usage = usage
        return func

    return register_wrapper


def register_module():
    def register_wrapper(clazz):
        clazz._active = True
        return clazz

    return register_wrapper


def run_daily(name: str, time: datetime.time):
    def register_wrapper(clazz):
        clazz._daily_run_name_decorator = name
        clazz._daily_run_time_decorator = time
        return clazz

    return register_wrapper


def register_message_watcher(filter: Filters):
    def register_wrapper(func):
        func._filter = filter
        return func

    return register_wrapper


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(obj, update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(obj, update, context, *args, **kwargs)

        return command_func
    return decorator
