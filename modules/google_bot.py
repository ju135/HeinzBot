from bs4 import BeautifulSoup
import urllib.request
from urllib.request import urlopen
from telegram import ChatAction, Update
from telegram.ext import CallbackContext
import json
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action


#@register_module()
class GoogleBot(AbstractModule):
    @register_command(command="image", text="Googlet noch an foto und schickts 👌🏼")
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    def get_image(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/image", update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&tbm=isch"
        print(url)
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/43.0.2357.134 Safari/537.36 "
        }
        soup = _get_soup(url, header)

        actual_images = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            actual_images.append((link, Type))
            break

        print("there are total", len(actual_images), "images")
        chat_id = update.message.chat_id
        if len(actual_images) < 1:
            update.message.reply_text("Leider nix gfunden ☹")
            return
        for i, (img, Type) in enumerate(actual_images):
            context.bot.send_photo(chat_id=chat_id, photo=img)

    @register_command(command="gif", text="Googlet noch an gif und schickts 👌🏼")
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    def get_gif(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter('/gif', update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&tbm=isch&tbs=itp:animated"
        print(url)
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/43.0.2357.134 Safari/537.36 "
        }
        soup = _get_soup(url, header)

        actual_images = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            actual_images.append((link, Type))
            break

        print("there are total", len(actual_images), "gifs")
        if len(actual_images) < 1:
            update.message.reply_text("Leider nix gfunden ☹️")
            return
        chat_id = update.message.chat_id
        for i, (img, Type) in enumerate(actual_images):
            context.bot.send_animation(chat_id=chat_id, animation=img)


def _get_soup(url, header):
    req = urllib.request.Request(url, headers=header)
    open_url = urlopen(req)
    soup = BeautifulSoup(open_url, "html.parser")
    return soup
