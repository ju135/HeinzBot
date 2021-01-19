import datetime
from functools import wraps
import logging
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


def register_message_watcher(filter: Filters):
    def register_wrapper(func):
        func._filter = filter
        return func

    return register_wrapper


def register_incline_cap():
    def register_wrapper(func):
        func._isInline = True
        return func

    return register_wrapper


def log_errors():
    def decorator(func):
        @wraps(func)
        def command_func(obj, update, context, *args, **kwargs):
            try:
                return func(obj, update, context, *args, **kwargs)
            except Exception as err:
                obj.log(text="Something happened in " + func.__name__, logging_type=logging.ERROR)
                obj.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
                update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")

        return command_func

    return decorator


def register_callback_query_handler(command, master=False):
    def register_wrapper(func):
        func._forCommand = command
        func._isMaster = master
        return func

    return register_wrapper


def register_scheduler(name: str):
    def register_wrapper(func):
        func._forScheduler = name
        return func

    return register_wrapper


def run_daily(name: str, time: datetime.time):
    def register_wrapper(clazz):
        clazz._daily_run_name_decorator = name
        clazz._daily_run_time_decorator = time
        return clazz

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


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
