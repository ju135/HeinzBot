import datetime


def register_command(command, text):
    def register_wrapper(func):
        func._command = command
        func._text = text
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