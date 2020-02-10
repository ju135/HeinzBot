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
        dp.add_handler(CommandHandler('wind', instance.wind))
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


    def __getClosestTime(self, increment):
        time = datetime.datetime.utcnow()
        diff = time.minute % increment
        time = time - datetime.timedelta(minutes=diff)

        timestring = time.strftime("%Y%m%d-%H%Mz")
        return timestring


    def __getKachelmannImage(self, pageURL):
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64)"
        }
        soup = self.get_soup(pageURL, header)

        imageurl = soup.find("meta", property="og:image")
        imageurl = imageurl["content"]
        return imageurl


    def __getRegion(self, region):
        errorMessage = ""
        if not region:
            errorMessage = "Parameter angeben bitte! Mögliche Regionen:\n" + ", ".join(KachelmannBot.REGIONEN.keys())
            return (region, errorMessage)
        try:
            region = KachelmannBot.REGIONEN[region.upper()]
        except KeyError:
            errorMessage = "De Region kenn i ned 🙄"
            return (region, errorMessage)

        return (region, errorMessage)


    def radar(self, bot, update):
        if not self.has_rights(update):
            return

        queryText = self.get_command_parameter("/radar", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/regenradar"
        timestring = self.__getClosestTime(5)
        pageURL = (baseURL + "/{}/{}.html").format(region, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=imageURL)


    def tracking(self, bot, update):
        if not self.has_rights(update):
            return

        queryText = self.get_command_parameter("/tracking", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            # invalid region
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/stormtracking"
        timestring = self.__getClosestTime(5)
        pageURL = (baseURL + "/{}/blitze-radarhd/{}.html").format(region, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=imageURL)


    def wind(self, bot, update):
        if not self.has_rights(update):
            return

        queryText = self.get_command_parameter("/wind", update)

        # split query into type and region
        syntaxErrorMessage = "I checks ned ganz, bitte schick ma dein command im Muster:\n`/wind (böen|mittel) <Region>`"
        windtype = ""
        region = ""
        try:
            windtype, region = queryText.split(maxsplit=2)
        except (ValueError, AttributeError) as e:
            # send syntax error
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return
        
        # get region
        region, errorMessage = self.__getRegion(region)
        if errorMessage != "":
            if region == "böen" or region == "böe" or region == "mittel":
                # mixed up parameters (/wind at böen), send syntax error
                bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                    text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                # else send unknown region error
                bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                    text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return
        
        # check type
        if windtype is not None and (windtype.lower() == 'böen' or windtype.lower() == 'böe'):
            windtype = "windboeen"
        elif windtype is not None and windtype.lower() == "mittel":
            windtype = "windrichtung-windmittel"
        else:
            # unknown type, send error
            errorMessage = "Mechadsd du Böen oder Mittelwind? Schick ma ans vo de zwa: 🌬️\n`/wind böen <Region>`\n`/wind mittel <Region>`"
            bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/analyse/superhd/"
        timestring = self.__getClosestTime(60)
        pageURL = (baseURL + "{}/{}/{}.html").format(region, windtype, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=imageURL)