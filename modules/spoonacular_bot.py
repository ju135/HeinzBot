import json
import requests
import telegram
from telegram import Update
from telegram.ext import  CallbackContext
from utils import api_key_reader
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command


@register_module()
class SpoonacularBot(AbstractModule):
    url = "https://api.spoonacular.com/"

    @register_command(command="meals",
                      short_desc="Returns random meal recipes to cook. 👨‍🍳🍽",
                      long_desc="Uses the spoonacular api in order to find 4 random meals and"
                                "returns them.",
                      usage=["/meals"])
    def random_receipt(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id(update)
        key = api_key_reader.read_key("spoon")
        extender = "{}recipes/random?apiKey={}&number=4".format(self.url, key)
        data = requests.get(extender)
        jsonData = json.loads(data.text)

        response = "Meals I found randomly \n"

        for recipe in jsonData['recipes']:
            response += "*" + recipe['title'] + "*" + "\n"
            response += recipe['sourceUrl'] + "\n"
            response += "\n"

        context.bot.send_message(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.MARKDOWN)
