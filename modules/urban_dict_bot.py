import json

import requests
import telegram
from telegram import Update
from telegram.ext import CallbackContext

from utils.api_key_reader import read_key
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command

URL = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"


def __remove_brackets(text: str) -> str:
    return text.replace('[', '').replace(']', '')


def __create_markdown_text(word: str, index: str, definition: str, example: str) -> str:
    # example formatting: *bold* _italic_ `fixed width font` [link](http://google.com).
    markdown_text = f"*{word}* _{index}_\n\n" \
                    f"{definition}\n\n" \
                    f"Example: \n_{example}_"

    return markdown_text


def _get_index_from_query(query: str) -> (int, str):
    words = query.split(" ")
    index = 0
    new_query = query

    if len(words) > 1:
        # check if the last word is an integer to use as index
        try:
            index = int(words[-1]) - 1
            if index < 0:
                index = 0
            new_query = query[:query.rindex(" ")]
        except:
            index = 0

    return index, new_query


def _get_dict_entry_and_send(index, query, bot, update) -> bool:
    querystring = {"term": query}
    headers = {
        'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
        'x-rapidapi-key': read_key("rapid_urban_dict_secret")
    }

    response = requests.request("GET", URL, headers=headers, params=querystring)

    if response is None or not response.ok:
        return False

    dict_data = json.loads(response.text)
    if "list" not in dict_data or len(dict_data['list']) < index + 1:
        return False

    try:
        data_object = dict_data['list'][index]
        definition = __remove_brackets(data_object['definition'])
        word = __remove_brackets(data_object['word'])
        example = __remove_brackets(data_object['example'])
        indexText = f"({index + 1}/{len(dict_data['list'])})"

        formatted_text = __create_markdown_text(word, indexText, definition, example)

        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=formatted_text, parse_mode=telegram.ParseMode.MARKDOWN)
        return True
    except:
        print("Exception when interpreting the urban dictionary json response")
        return False


@register_module()
class UrbanDictBot(AbstractModule):
    @register_command(command="whatis",
                      short_desc="Kennst di bei and wort oda a phrasn ned aus? I hüf da weita. 🤓",
                      long_desc="", usage=[""])
    def what_is(self, update: Update, context: CallbackContext):


        query = self.get_command_parameter("/whatis", update)

        if query is None:
            update.message.reply_text('Wos wüsd wissn?')
            return

        # find the entry index
        index, query = _get_index_from_query(query)

        success = _get_dict_entry_and_send(index, query, context.bot, update)
        if not success:
            update.message.reply_text("Leider nix gfunden...")
