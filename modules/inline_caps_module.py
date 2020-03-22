import json
import random
from abc import ABC

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_incline_cap


class InlineCaps(AbstractModule):

    @register_incline_cap()
    def inline_caps(self, update: Update, context: CallbackContext):
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
        context.bot.answer_inline_query(update.inline_query.id, results)
