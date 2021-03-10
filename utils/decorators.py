import datetime
from functools import wraps
import logging
import sys
from inspect import getframeinfo
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
                frame_info = _get_caller_frame_info()
                line = frame_info.lineno
                function_name = frame_info.function
                file_name = frame_info.filename.split('/')[-1].split('.')[0]
                caller_description = f"{file_name}:{function_name}:{line}>"
                obj.log_with_caller_description(text=str(err),
                                                caller_description=caller_description,
                                                logging_type=logging.ERROR)
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


def _get_caller_frame_info():
    traceback = sys.exc_info()[2]
    # start with the next traceback since the first is the decorator itself
    tb = traceback.tb_next
    frame_info = getframeinfo(tb)
    # there could be multiple decorators on top of each other, so iterate through them
    while frame_info.filename is __file__ and tb.tb_next is not None:
        tb = tb.tb_next
        frame_info = getframeinfo(tb)
    return frame_info
