import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup


def inspire(bot, update):
    url = "https://inspirobot.me/api?generate=true"
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }
    soup = get_soup(url, header)
    chat_id = update.message.chat_id
    img = soup.text
    bot.send_photo(chat_id=chat_id, photo=img)


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command+" "):
        return text[len(command)+1:]
    if text.startswith(command + b + " "):
        return text[len(command+b) + 1:]


def get_soup(url, header):
    req = urllib.request.Request(url, headers=header)
    openurl = urlopen(req)
    soup = BeautifulSoup(openurl, "html.parser")
    return soup