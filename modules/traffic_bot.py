import telegram
import logging
import feedparser
import time

from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors

@register_module()
class TrafficBot(AbstractModule):
    @register_command(command="traffic", short_desc="Gets the current traffic information",
                      long_desc="",
                      usage=["/traffic"])
    @log_errors()
    @send_action(action=ChatAction.TYPING)
    def traffic(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/trans", update)

        self.log(text="Getting items from RSS feed..", logging_type=logging.INFO)
        rssFeed = feedparser.parse("https://www.oeamtc.at/feeds/verkehr/oberoesterreich")
        #print (rssFeed.entries)

        feedUpdateTime = time.strftime("%a, %d\. %B %H:%M", rssFeed.feed.updated_parsed)

        message = "Verkehrsupdate von _" + feedUpdateTime + "_"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN_V2)