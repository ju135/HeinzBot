import json
import logging
import requests

from telegram import ChatAction, Update
from telegram.ext import CallbackContext
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action, log_errors


@register_module()
class GoogleBot(AbstractModule):
    max_amount_query_attempts = 10

    @register_command(command="image", short_desc="Googlet noch an foto und schickts 👌🏼", long_desc="", usage=[""])
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    @log_errors()
    def get_image(self, update: Update, context: CallbackContext):
        imageCounter = 0

        query = self.get_command_parameter("/image", update)
        if not query:
            update.message.reply_text("Parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)
        url = "https://www.googleapis.com/customsearch/v1?searchType=image&key=" + self.get_api_key(
            "google_key") + "&cx=" + self.get_api_key("google_cx") + f"&num={self.max_amount_query_attempts}&q=" + query
        response = self.retrieveJsonResponse(url)

        if int(response["searchInformation"]["totalResults"]) == 0:
            update.message.reply_text("Leider nix gfunden ☹")
            return
        else:
            success = self.queryImage(response, update, context, "Image", imageCounter)
            imageCounter = imageCounter + 1
            while success is False and imageCounter < self.max_amount_query_attempts:
                success = self.queryImage(response, update, context, "Image", imageCounter)
                imageCounter = imageCounter + 1
            if success is False:
                self.log(text=f"All {self.max_amount_query_attempts} queried image urls failed. Stopping.", logging_type=logging.INFO)
                update.message.reply_text(
                    f"Jetzt duad sis, i hob {self.max_amount_query_attempts} Ergebnisse probiert, olle gengan nimma ☹ Probier bitte an aundan Suchbegriff!")

    @register_command(command="gif", short_desc="Googlet noch an gif und schickts 👌🏼", long_desc="", usage=[""])
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    @log_errors()
    def get_gif(self, update: Update, context: CallbackContext):
        imageCounter = 0

        query = self.get_command_parameter('/gif', update)
        if not query:
            update.message.reply_text("Parameter angeben bitte...")
            return
        query = self.percent_encoding(query).split()
        query = '+'.join(query)
        url = "https://www.googleapis.com/customsearch/v1?searchType=image&imgType=animated&key=" + self.get_api_key(
            "google_key") + "&cx=" + self.get_api_key("google_cx") + f"&num={self.max_amount_query_attempts}&q=" + query
        response = self.retrieveJsonResponse(url)

        if int(response["searchInformation"]["totalResults"]) == 0:
            update.message.reply_text("Leider nix gfunden ☹")
            return
        else:
            success = self.queryImage(response, update, context, "Gif", imageCounter)
            imageCounter = imageCounter + 1

            while success is False and imageCounter < self.max_amount_query_attempts:
                success = self.queryImage(response, update, context, "Gif", imageCounter)
                imageCounter = imageCounter + 1
            if success is False:
                self.log(text=f"All {self.max_amount_query_attempts} queried gif urls failed. Stopping.", logging_type=logging.INFO)
                update.message.reply_text(
                    f"Jetzt duad sis, i hob {self.max_amount_query_attempts} Ergebnisse probiert, olle gengan nimma ☹ Probier bitte an aundan Suchbegriff!")

    def queryImage(self, response, update, context, queryType, counter):
        imageUrl = response["items"][counter]["link"]
        self.log(text=queryType + " url is: " + imageUrl, logging_type=logging.INFO)

        if self.is_valid_url_image(imageUrl, update):
            chat_id = update.message.chat_id
            try:
                if queryType == "Image":
                    self.send_and_save_picture(update=update, context=context,
                                               image_url=imageUrl,
                                               command="/image",
                                               caption="")

                    # context.bot.send_photo(chat_id=chat_id, photo=imageUrl)
                else:
                    self.send_and_save_video(update=update, context=context,
                                             vide_url=imageUrl,
                                             command="/gif",
                                             caption="")

                return True
            except Exception as e:
                # some search results return huge images which aren't minimized. Telegram can't handle huge images
                # unless they are sent as file. e.g. /image Krüger (tested on 06.12.2020) produces this exception
                self.log(text="Image too large, Telegram can't handle so much pixels! Error: " + str(e),
                         logging_type=logging.ERROR)
                return False

        else:
            self.log(
                text="Image Url wrong, image not available anymore or invalid image type which Telegram can't handle!",
                logging_type=logging.INFO)
            return False

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
                # content-type is wrong
                return False
            else:
                # http status code wrong -> url suburl moved/not available anymore / restricted access etc.
                return False

        except Exception as e:
            # request crashes if url not available (request timeout)
            self.log(text="Image Url wrong, webserver seems to be not accessible! Error: " + str(e),
                     logging_type=logging.ERROR)
