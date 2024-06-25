import telegram
import requests
import json
import logging
import feedparser
import time
import locale

from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from datetime import datetime
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors

@register_module()
class TrafficBot(AbstractModule):
    @register_command(command="traffic", short_desc="Gets the current traffic information 👷🏼⚠️",
                      long_desc="Searches for current traffic information in RSS feed of ÖAMTC and webpage of Life Radio. "
                                "Standard location is Upper Austria, but can be defined by optional parameter `[state]` ",
                      usage=["/traffic\n/traffic [oö]\n/traffic Salzburg"])
    @send_action(action=ChatAction.TYPING)
    @log_errors()
    def traffic(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/traffic", update)

        ## sets locale to systems locale, needed for time printing
        locale.setlocale(locale.LC_TIME, "")

        ## begin ÖAMTC

        headline1 = "*ÖAMTC*\n"
        oeamtc = self.gatherOeamtcData(text)
        oeamtc = headline1 + oeamtc

        ## end ÖAMTC

        ## begin LifeRadio
        liferadio = ""
        if not text or text.casefold() == "ooe" or text.casefold() == "oö" or text.casefold() == "oberoesterreich" or text.casefold() == "Oberösterreich":
            headline2 = "\n*Life Radio*\n"
            liferadio = self.gatherLifeRadioData()
            liferadio = headline2 + liferadio

        ## end LifeRadio

        message = oeamtc + liferadio
        self.log(text="Final message: " + message, logging_type=logging.DEBUG)
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN_V2)

    def gatherOeamtcData(self, text):
        self.log(text="Getting items from OEAMTC RSS feed..", logging_type=logging.INFO)
        feedlink = self.locationSwitcher(text)
        rssFeed = feedparser.parse(feedlink)

        feedUpdateTime = rssFeed.feed.updated_parsed
        feedUpdateTime = time.strftime("%a, %d. %b %H:%M", feedUpdateTime)
        feedUpdateTime = self.escape_markdown_characters(feedUpdateTime)

        oeamtcMessageHeader = "Verkehrsupdate von _" + feedUpdateTime + "_\n"
        oeamtcMessage = ""

        trafficdata = []
        for item in rssFeed.entries:
            title = category = summary = pubDate = ""

            # check if data even exists (sometimes no category is given for instance)
            if 'title' in item:
                title = item.title
            if 'tags' in item:
                category = item.tags[0].term
            if 'summary' in item:
                summary = item.summary
            if 'published_parsed' in item:
                pubDate = item.published_parsed
            relevantData = [title, category, summary, pubDate]
            trafficdata.append(relevantData)

        trafficdata.sort(key=self.returnEntryDate, reverse=True)

        # print last 4 entries
        for i, entry in enumerate(trafficdata):
            if i < 4:
                icon = "❗️ "
                if entry[1] == "Baustelle":
                    icon = "👷🏼 "
                if entry[1] == "Verkehrsbehinderung":
                    icon = "⚠️ "
                if entry[1] == "Sperre":
                    icon = "⛔️ "
                if entry[1] == "Schneekette":
                    icon = "❄️ "

                oeamtcMessage += icon

                # check if entry has current day, otherwise print day and time
                if time.strftime("%d/%m/%Y", entry[3]) == time.strftime("%d/%m/%Y", time.localtime()):
                    oeamtcMessage += time.strftime("%H:%M", entry[3]) + "\n"
                else:
                    oeamtcMessage += time.strftime("%d. %b, %H:%M", entry[3]) + "\n"

                oeamtcMessage += entry[0] + "; "
                oeamtcMessage += entry[2] + "\n\n"
            else:
                message = oeamtcMessage[:-4] #removes double line breaks after last message
                break

        return oeamtcMessageHeader + self.escape_markdown_characters(oeamtcMessage)

    def gatherLifeRadioData(self):
        self.log(text="Getting items from Life Radio website..", logging_type=logging.INFO)
        r = requests.get("https://www.liferadio.at/api/traffic")
        traffic_data = json.loads(r.text)

        traffic_update_time = traffic_data["createdAt"]

        traffic_info = ""
        # if no information provided, there is always a single message with text saying "no information"
        if "from" not in traffic_data["messages"][0]:
            traffic_info = "keine Meldungen"
        for trafficEntry in traffic_data["messages"]:
            if "from" in trafficEntry:
                traffic_info += trafficEntry["text"] + "\n"

        traffic_info = self.escape_markdown_characters(traffic_info)

        if traffic_update_time is not None:
            traffic_update_time = datetime.fromisoformat(traffic_update_time)
            traffic_update_time = traffic_update_time.strftime("%a, %d\. %b, %H:%M")

        return "Verkehrsupdate von _" + traffic_update_time + "_\n" + traffic_info

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