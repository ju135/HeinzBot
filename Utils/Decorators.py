def register(command, text):
    def register_wrapper(func):
        func._command = command
        func._text = text
        return func

    return register_wrapper
