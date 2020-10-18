import json
import logging
import requests

from telegram import ChatAction, Update
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors


@register_module()
class GoogleBot(AbstractModule):
    @register_command(command="image", short_desc="Googlet noch an foto und schickts 👌🏼", long_desc="", usage=[""])
    @log_errors()
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    def get_image(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/image", update)
        if not query:
            update.message.reply_text("Parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)

        url = "https://www.googleapis.com/customsearch/v1?searchType=image&key=" + self.get_api_key("google_key") + "&cx=" + self.get_api_key("google_cx") + "&num=1&q=" + query
        response = self.retrieveJsonResponse(url)

        if int(response["searchInformation"]["totalResults"]) == 0:
            update.message.reply_text("Leider nix gfunden ☹")
            return
        else:
            imageUrl = response["items"][0]["link"]
            self.log(text="Image url is: " + imageUrl, logging_type=logging.INFO)
            chat_id = update.message.chat_id
            context.bot.send_photo(chat_id=chat_id, photo=imageUrl)

    @register_command(command="gif", short_desc="Googlet noch an gif und schickts 👌🏼", long_desc="", usage=[""])
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    def get_gif(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter('/gif', update)
        if not query:
            update.message.reply_text("Parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)
        url = "https://www.googleapis.com/customsearch/v1?searchType=image&imgType=animated&key=" + self.get_api_key("google_key") + "&cx=" + self.get_api_key("google_cx") + "&num=1&q=" + query
        response = self.retrieveJsonResponse(url)

        if int(response["searchInformation"]["totalResults"]) == 0:
            update.message.reply_text("Leider nix gfunden ☹")
            return
        else:
            imageUrl = response["items"][0]["link"]
            self.log(text="Gif url is: " + imageUrl, logging_type=logging.INFO)
            chat_id = update.message.chat_id
            context.bot.send_animation(chat_id=chat_id, animation=imageUrl)

    def retrieveJsonResponse(self, url):
        response = requests.get(url)
        return json.loads(response.text)
