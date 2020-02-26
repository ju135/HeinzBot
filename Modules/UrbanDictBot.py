import telegram
from telegram.ext import CommandHandler
from Modules.DefaultModule import DefaultModule
import requests
import json
from APIKeyReader import read_key

url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"


def remove_brackets(text: str) -> str:
    return text.replace('[', '').replace(']', '')


def create_markdown_text(word: str, index: str, definition: str, example: str) -> str:
    # example formatting: *bold* _italic_ `fixed width font` [link](http://google.com).
    markdown_text = f"*{word}* _{index}_\n\n" \
                    f"{definition}\n\n" \
                    f"Example: \n_{example}_"

    return markdown_text


def get_index_from_query(query: str) -> (int, str):
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


def get_dict_entry_and_send(index, query, bot, update) -> bool:
    querystring = {"term": query}
    headers = {
        'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
        'x-rapidapi-key': read_key("rapid_urban_dict_secret")
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response is None or not response.ok:
        return False

    dict_data = json.loads(response.text)
    if "list" not in dict_data or len(dict_data['list']) < index + 1:
        return False

    try:
        data_object = dict_data['list'][index]
        definition = remove_brackets(data_object['definition'])
        word = remove_brackets(data_object['word'])
        example = remove_brackets(data_object['example'])
        indexText = f"({index+1}/{len(dict_data['list'])})"

        formatted_text = create_markdown_text(word, indexText, definition, example)

        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=formatted_text, parse_mode=telegram.ParseMode.MARKDOWN)
        return True
    except:
        print("Exception when interpreting the urban dictionary json response")
        return False


class UrbanDictBot(DefaultModule):
    def add_command(self, dp):
        instance = UrbanDictBot()
        dp.add_handler(CommandHandler('whatis', instance.what_is))
        return dp

    def what_is(self, bot, update):
        if not self.has_rights(update):
            return

        query = self.get_command_parameter("/whatis", update)

        if query is None:
            update.message.reply_text('Wos wüsd wissn?')
            return

        # find the entry index
        index, query = get_index_from_query(query)

        success = get_dict_entry_and_send(index, query, bot, update)
        if not success:
            update.message.reply_text("Leider nix gfunden...")
