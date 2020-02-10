import telegram
from telegram.ext import CommandHandler
import json
import requests
import datetime

import APIKeyReader

from Modules.DefaultModule import DefaultModule


class KachelmannBot(DefaultModule):

    def add_command(self, dp):
        instance = KachelmannBot()
        dp.add_handler(CommandHandler('radar', instance.radar))
        dp.add_handler(CommandHandler('tracking', instance.tracking))
        return dp
    
    REGIONEN = {
        "BR":   "braunau-am-inn",
        "EF":   "eferding",  	
        "FR":   "freistadt",
        "GM":   "gmunden",	
        "GR":   "grieskirchen",
        "KI":   "kirchdorf-an-der-krems",
        "L" :   "linz",
        "LL":   "linz-land",	
        "PE":   "perg", 
        "RI":   "ried-im-innkreis",
        "RO":   "rohrbach-im-muehlkreis",
        "SD":   "schaerding",
        "SR":   "steyr",
        "SE":   "steyr-land",
        "UU":   "urfahr-umgebung",
        "VB":   "voecklabruck",
        "WE":   "wels",
        "WL":   "wels-land",
        "OÖ":   "oberoesterreich",
        "NÖ":   "niederoesterreich",
        "STMK": "steiermark",
        "WZ": "weiz",
        "G": "graz",
        "BM": "bruck-an-der-mur",
        "LE": "leoben",
        "LI": "liezen",
        "W":    "wien",
        "B":    "burgenland",
        "SBG":  "salzburg",
        "T":    "tirol",
        "V":    "vorarlberg",
        "K":    "kaernten",
        "AT":   "oesterreich"
    }


    def __get5MinTime(self):
        time = datetime.datetime.utcnow()
        diff = time.minute % 5
        time = time - datetime.timedelta(minutes=diff)

        timestring = time.strftime("%Y%m%d-%H%M")
        return timestring


    def __getKachelmannImage(self, pageURL):
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64)"
        }
        soup = self.get_soup(pageURL, header)

        imageurl = soup.find("meta", property="og:image")
        imageurl = imageurl["content"]
        return imageurl


    def __getRegion(self, queryText):
        location = ""
        errorMessage = ""
        if not queryText:
            errorMessage = "Parameter angeben bitte! Mögliche Regionen:\n" + ", ".join(KachelmannBot.REGIONEN.keys())
            return (location, errorMessage)
        try:
            location = KachelmannBot.REGIONEN[queryText.upper()]
        except KeyError:
            errorMessage = "De Region kenn i ned 🙄"
            return (location, errorMessage)

        return (location, errorMessage)


    def radar(self, bot, update):
        if not self.has_rights(update):
            return

        queryText = self.get_command_parameter("/radar", update)

        location, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/regenradar"
        timestring = self.__get5MinTime()
        pageURL = (baseURL + "/{}/{}z.html").format(location, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=imageURL)


    def tracking(self, bot, update):
        if not self.has_rights(update):
            return

        queryText = self.get_command_parameter("/tracking", update)

        location, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/stormtracking"
        timestring = self.__get5MinTime()
        pageURL = (baseURL + "/{}/blitze-radarhd/{}z.html").format(location, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=imageURL)