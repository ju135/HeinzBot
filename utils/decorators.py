def register_command(command, text):
    def register_wrapper(func):
        func._command = command
        func._text = text
        return func

    return register_wrapper


def register_module(active: bool, key: str):
    def register_wrapper(clazz):
        clazz._active = active
        clazz._key = key
        return clazz

    return register_wrapper
