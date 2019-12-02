from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.request import urlopen
from googleapiclient.discovery import build
from APIKeyReader import read_key
import logging
import json
import datetime

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

regionen = {
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
    "SE":   "steyr",
    "SR":   "steyr-land",
    "UU":   "urfahr-umgebung",
    "VB":   "voecklabruck",
    "WE":   "wels",
    "WL":   "wels-land",
    "OÖ":   "oberoesterreich",
    "NÖ":   "niederoesterreich",
    "STMK": "steiermark",
    "W":    "wien",
    "B":    "burgenland",
    "SBG":  "salzburg",
    "T":    "tirol",
    "V":    "vorarlberg",
    "K":    "kaernten",
    "AT":   "oesterreich"
}


def radar(bot, update):
    global regionen
    query = get_command_parameter("/radar", update)
    if not query:
        update.message.reply_text("Parameter angeben bitte! Mögliche Regionen:\n" + ", ".join(regionen.keys()))
        return

    time = datetime.datetime.utcnow()
    diff = time.minute % 5
    time = time - datetime.timedelta(minutes=diff)

    timestring = time.strftime("%Y%m%d-%H%M")

    url = "https://kachelmannwetter.com/at/regenradar/freistadt/{}z.html".format(timestring)
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64)"
    }
    soup = get_soup(url, header)

    imageurl = soup.find("meta", property="og:image")
    imageurl = imageurl["content"]
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=imageurl)


def get_soup(url, header):
    req = urllib.request.Request(url, headers=header)
    openurl = urlopen(req)
    soup = BeautifulSoup(openurl, "html.parser")
    return soup


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command+" "):
        return text[len(command)+1:]
    if text.startswith(command + b + " "):
        return text[len(command+b) + 1:]


