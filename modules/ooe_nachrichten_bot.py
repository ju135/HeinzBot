import requests
from xml.dom import minidom
from telegram import Update
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command


@register_module()
class OENewsBot(AbstractModule):
    @register_command(command="news", short_desc="Gets the latest austrian news. 📰",
                      long_desc="Fetches the latest news from [OÖNachrichten](https://www.nachrichten.at/) "
                                "and sends it. The amount of news can be specified. "
                                "If not specified, only one article is sent.",
                      usage=["/news", "/news $amount", "/news 4"])
    def get_newest_news(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/news", update)
        if query is None or query.isdigit():
            r = requests.get("https://www.nachrichten.at/storage/rss/rss/nachrichten.xml")
            parsed = minidom.parseString(r.text)
            try:
                text = ""
                if query is not None:
                    if int(query) > 4:
                        query = 4
                    for i in range(int(query)):
                        newest = parsed.getElementsByTagName("item")[i]
                        title = newest.getElementsByTagName("title")[0].firstChild.data
                        link = newest.getElementsByTagName("link")[0].firstChild.data
                        descr = newest.getElementsByTagName("description")[0].firstChild.data
                        text += title + "\n" + link + "\n" + descr + "\n \n \n"
                else:
                    newest = parsed.getElementsByTagName("item")[0]
                    title = newest.getElementsByTagName("title")[0].firstChild.data
                    link = newest.getElementsByTagName("link")[0].firstChild.data
                    descr = newest.getElementsByTagName("description")[0].firstChild.data
                    text += title + "\n" + link + "\n" + descr + "\n"

                chat_id = self.get_chat_id(update)
                context.bot.send_message(chat_id=chat_id, text=text)
            except:
                context.bot.message.reply_text("Leider nix gfunden ☹️")
        else:
            context.bot.message.reply_text("Du musst a Zahl eingeben du Floschn!️")
