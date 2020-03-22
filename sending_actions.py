from functools import wraps
import telegram


def send_photo_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(*args, **kwargs):
        bot, update = args
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        return func(bot, update, **kwargs)

    return command_func


def send_video_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(*args, **kwargs):
        bot, update = args
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.UPLOAD_VIDEO)
        return func(bot, update, **kwargs)
    return command_func


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(obj, update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(obj, update, context, *args, **kwargs)

        return command_func

    return decorator