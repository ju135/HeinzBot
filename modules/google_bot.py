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

            if self.is_valid_url_image(imageUrl, update):
                chat_id = update.message.chat_id
                context.bot.send_photo(chat_id=chat_id, photo=imageUrl)

            else:
                self.log(text="Image Url wrong, image not available anymore or invalid image type which Telegram can't handle!", logging_type=logging.INFO)
                update.message.reply_text("Des Büdl gibts scho nimma oda Telegram kau den Büdl Typ ned.. ☹ Probier an aundan Suchbegriff!")

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

            if self.is_valid_url_image(imageUrl, update):
                chat_id = update.message.chat_id
                context.bot.send_animation(chat_id=chat_id, animation=imageUrl)

            else:
                self.log(text="Image Url wrong, image not available anymore or invalid image type which Telegram can't handle!", logging_type=logging.INFO)
                update.message.reply_text("Des Büdl gibts scho nimma oda Telegram kau den Büdl Typ ned.. ☹ Probier an aundan Suchbegriff!")

    def retrieveJsonResponse(self, url):
        response = requests.get(url)
        return json.loads(response.text)

    def is_valid_url_image(self, imageUrl, update):
        # sadly svgs are not supported by telegram :(
        allowed_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")

        try:
            imageUrlResponse = requests.head(imageUrl)
            if imageUrlResponse.status_code < 400:
                if imageUrlResponse.headers["content-type"] in allowed_formats:
                    return True
                return False
            else:
                return False

        except Exception as e:
            self.log(text="Image Url wrong, webserver seems to be not accessible! Error: " + str(e), logging_type=logging.ERROR)
            update.message.reply_text("Mamamia, do hod Google nu a uroide Url gecacht, den Webserver gibts scho laung nimma.. Probier an aundan Suchbegriff!")
