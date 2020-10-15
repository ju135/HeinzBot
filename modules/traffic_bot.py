import telegram
import logging
import feedparser
import time
import locale

from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors

@register_module()
class TrafficBot(AbstractModule):
    @register_command(command="traffic", short_desc="Gets the current traffic information 👷🏼⚠️",
                      long_desc="Searches for current traffic information in RSS feed of ÖAMTC. "
                                "Standard location is Upper Austria, but can be defined by optional parameter `[state]` ",
                      usage=["/traffic\n/traffic [oö]\n/traffic Salzburg"])
    @log_errors()
    @send_action(action=ChatAction.TYPING)
    def traffic(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/traffic", update)

        ## sets locale to systems locale, needed for time printing
        locale.setlocale(locale.LC_TIME, "")

        ## begin ÖAMTC

        message = "*ÖAMTC*\n"
        message = self.gatherOeamtcData(message, text)

        ## end ÖAMTC

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN_V2)

    def gatherOeamtcData(self, message, text):
        self.log(text="Getting items from OEAMTC RSS feed..", logging_type=logging.INFO)
        feedlink = self.locationSwitcher(text)
        rssFeed = feedparser.parse(feedlink)

        feedUpdateTime = rssFeed.feed.updated_parsed
        feedUpdateTime = time.strftime("%a, %d\. %b %H:%M", feedUpdateTime)
        #### caution, strftime function depends on system settings whether time zone is correct or not!

        message += "Verkehrsupdate von _" + feedUpdateTime + "_\n"

        trafficdata = []
        for item in rssFeed.entries:
            title = category = summary = pubDate = ""

            # check if data even exists (sometimes no category is given for instance)
            if 'title' in item:
                title = item.title.replace("-", "\-").replace(".", "\.")
            if 'tags' in item:
                category = item.tags[0].term.replace("-", "\-").replace(".", "\.")
            if 'summary' in item:
                summary = item.summary.replace("-", "\-").replace(".", "\.")
            if 'published_parsed' in item:
                pubDate = item.published_parsed
            relevantData = [title, category, summary, pubDate]
            trafficdata.append(relevantData)

        trafficdata.sort(key=self.returnEntryDate, reverse=True)

        # print last 4 entries
        for i, entry in enumerate(trafficdata):
            if i < 4:
                if entry[1] == "Baustelle":
                    message += "👷🏼 "
                if entry[1] == "Verkehrsbehinderung":
                    message += "⚠️ "
                if entry[1] == "Sperre":
                    message += "⛔️ "
                if entry[1] == "Schneekette":
                    message += "❄️ "

                message += time.strftime("%H:%M", entry[3]) + "\n"
                message += entry[0] + "; "
                message += entry[2] + "\n\n"
            else:
                break

        return message

    def locationSwitcher(self, location):
        url = "https://www.oeamtc.at/feeds/verkehr/"
        if location == "nö" or location == "NÖ" or location == "noe" or location == "niederoesterreich" or location == "Niederösterreich":
            return url + "niederoesterreich"
        elif location == "s" or location == "S" or location == "salzburg" or location == "Salzburg":
            return url + "salzburg"
        elif location == "k" or location == "K" or location == "kaernten" or location == "Kärnten":
            return url + "kaernten"
        elif location == "t" or location == "T" or location == "tirol" or location == "Tirol":
            return url + "tirol"
        elif location == "w" or location == "W" or location == "wien" or location == "Wien":
            return url + "wien"
        elif location == "b" or location == "B" or location == "burgenland" or location == "Burgenland":
            return url + "burgenland"
        elif location == "st" or location == "stmk" or location == "ST" or location == "STMK" or location == "steiermark" or location == "Steiermark":
            return url + "steiermark"
        elif location == "v" or location == "V" or location == "vorarlberg" or location == "Vorarlberg":
            return url + "vorarlberg"
        else:
            return url + "oberoesterreich"

    def returnEntryDate(self, entry):
        return entry[3]