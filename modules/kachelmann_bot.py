import datetime
import urllib
from urllib.request import urlopen

import bs4
import telegram
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command


@register_module()
class KachelmannBot(AbstractModule):
    REGIONEN = {
        "BR": "braunau-am-inn",
        "EF": "eferding",
        "FR": "freistadt",
        "GM": "gmunden",
        "GR": "grieskirchen",
        "KI": "kirchdorf-an-der-krems",
        "L": "linz",
        "LL": "linz-land",
        "PE": "perg",
        "RI": "ried-im-innkreis",
        "RO": "rohrbach-im-muehlkreis",
        "SD": "schaerding",
        "SR": "steyr",
        "SE": "steyr-land",
        "UU": "urfahr-umgebung",
        "VB": "voecklabruck",
        "WE": "wels",
        "WL": "wels-land",
        "OÖ": "oberoesterreich",
        "NÖ": "niederoesterreich",
        "STMK": "steiermark",
        "WZ": "weiz",
        "G": "graz",
        "BM": "bruck-an-der-mur",
        "LE": "leoben",
        "LI": "liezen",
        "W": "wien",
        "B": "burgenland",
        "SBG": "salzburg",
        "T": "tirol",
        "V": "vorarlberg",
        "K": "kaernten",
        "AT": "oesterreich"
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

    def get_soup(self, url, header):
        req = urllib.request.Request(url, headers=header)
        open_url = urlopen(req)
        soup = bs4.BeautifulSoup(open_url, "html.parser")
        return soup

    @register_command(command="radar", short_desc="Shows the rain radar of a region. 🌧",
                      long_desc="This command returns an image containing the current "
                                "rain conditions of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(REGIONEN.keys()),
                      usage=["/radar $region-abbreviation", "/radar FR"])
    def radar(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/radar", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
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
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)

    @register_command(command="tracking", short_desc="Storm-tracking of a region. ⛈⚡️",
                      long_desc="This command returns an image containing the current "
                                "storm-tracking information of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(REGIONEN.keys()),
                      usage=["/tracking $region-abbreviation", "/tracking AT"])
    def tracking(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/tracking", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            # invalid region
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
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
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)

    @register_command(command="wind", short_desc="Shows the wind gusts of a region. 💨🌬",
                      long_desc="This command returns an image containing the current "
                                "wind direction or wind gust information of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(REGIONEN.keys()),
                      usage=["/wind (böen|mittel) $region", "/wind böen AT", "/wind mittel WZ"])
    def wind(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/wind", update)

        # split query into type and region
        syntaxErrorMessage = "I checks ned ganz, bitte schick ma dein command im Muster:\n`/wind (böen|mittel) <Region>`"
        windtype = ""
        region = ""
        try:
            windtype, region = queryText.split(maxsplit=2)
        except (ValueError, AttributeError) as e:
            # send syntax error
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # get region
        region, errorMessage = self.__getRegion(region)
        if errorMessage != "":
            if region == "böen" or region == "böe" or region == "mittel":
                # mixed up parameters (/wind at böen), send syntax error
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                         text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                # else send unknown region error
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
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
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
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
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)
