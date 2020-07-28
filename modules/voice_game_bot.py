import base64
import json
import logging
import os
import random
import requests


from gtts import gTTS
from gtts.lang import tts_langs
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, send_action

VOICE_GAME_FILE = "utils/voice_game_data.json"
quote_api_url = "https://api.forismatic.com/api/1.0/?method=getQuote&lang=en&format=json"

@register_module()
class VoiceGameBot(AbstractModule):
    @register_command(command="voicegame", short_desc="Play a voice quiz.",
                      long_desc="Sends a known english quote spoken in a random language. "
                                "Use the /va command to guess the quote and win the quiz.",
                      usage=["/voicegame [solve]", "/voicegame", "/voicegame solve"])
    @send_action(action=ChatAction.RECORD_AUDIO)
    def voice_game(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        command = self.get_command_parameter("/voicegame", update)
        languages = tts_langs("com")
        if command is None:
            game_data = _read_game_data(chat_id)
            if game_data is not None:
                quote_text = game_data['quoteText']
                language = game_data["language"]
                caption = f"The current quiz of this {languages[language].lower()} person was not answered yet.\n" \
                          f"Keep on guessing with '/va [guess]' or call '/voicegame solve'."
                self._send_voice_message(quote_text, caption, language, context, update)
                return
        elif command.lower() == "solve":
            game_data = _read_game_data(chat_id)
            if game_data is not None:
                author = "unknown"
                if "quoteAuthor" in game_data:
                    author = game_data["quoteAuthor"]
                update.message.reply_markdown(f"The solution is: \n\n"
                                              f"*{game_data['quoteText']}*\n"
                                              f"_Quote by {author}_")
                _write_game_data(None, chat_id)
                return

        # read random quote
        response = requests.request("GET", quote_api_url)
        if response is None or not response.ok:
            return False

        language = random.choice(list(languages.keys()))
        dict_data = json.loads(response.text)
        if "quoteText" not in dict_data or len(dict_data['quoteText']) < 1:
            return False

        quote_text = dict_data['quoteText']
        dict_data["language"] = language
        _write_game_data(dict_data, chat_id)
        caption = f"What is this {tts_langs('com')[language].lower()} person saying?"
        self._send_voice_message(quote_text, caption, language, context, update)

    @register_command(command="va", short_desc="Voice game answer command.",
                      long_desc="Write your answer to the voice game question and see if it's correct. "
                                "You can also guess parts of the quote - the guess has to be at least 4 characters.",
                      usage=["/va [solution|guess]", "/va capacity", "/va Strength does not come from physical capacity. It comes from an indomitable will."])
    def voice_answer(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        text = self.get_command_parameter("/va", update)
        if text is None:
            update.message.reply_text("wut?")
            return
        answer = _get_alphanumeric_lower_case(text)
        solution_data = _read_game_data(chat_id)
        if solution_data is None or "quoteText" not in solution_data:
            update.message.reply_markdown("There is no voice game running in this chat. Start one with /voicegame.")
            return

        solution = solution_data["quoteText"]
        author = "unknown"
        if "quoteAuthor" in solution_data:
            author = solution_data["quoteAuthor"]
        if answer == _get_alphanumeric_lower_case(solution):
            update.message.reply_markdown(f"Correct!\n\n" 
                                          f"*{solution}*\n"
                                          f"_Quote by {author}_")
            _write_game_data(None, chat_id)
        elif len(answer) > 3 and answer in solution.lower():
            update.message.reply_markdown("*Moist* - This part does exist in the quote.")
        else:
            update.message.reply_text("wrong.")

    def _send_voice_message(self, message, caption, language, context, update):
        try:
            self.log(text="Trying to say something", logging_type=logging.DEBUG)

            if message is not None:
                fn = _makeBase64Filename(message) + ".mp3"

                words = gTTS(text=message, lang=language, slow=False)
                words.save(fn)
                audio = open(fn, 'rb')
                context.bot.send_voice(chat_id=update.message.chat_id, voice=audio, reply_to_message_id=update.message.message_id,
                                       caption=caption)
                try:
                    os.remove(fn)
                except Exception as err:
                    self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            else:
                update.message.reply_text("Wos?")
        except Exception as err:
            self.log(text="Error: {0}".format(err), logging_type=logging.ERROR)
            update.message.reply_text("Irgendwos is passiert bitte schau da in Log au!")


def _get_alphanumeric_lower_case(text: str) -> str:
    alphanumeric = [character for character in text if character.isalnum()]
    alphanumeric = "".join(alphanumeric)
    return alphanumeric.lower()


def _makeBase64Filename(text):
    message_bytes = str.encode(text, encoding='ascii', errors='ignore')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message[0:10]


def _read_game_data(chat_id):
    chat_id = f"{chat_id}"
    json_object = _read_game_data_json_content()
    if chat_id in json_object:
        return json_object[chat_id]
    return None


def _write_game_data(json_quote, chat_id):
    json_object = _read_game_data_json_content()
    json_object[f"{chat_id}"] = json_quote
    file = open(VOICE_GAME_FILE, "w")
    json.dump(json_object, file)
    file.close()


def _read_game_data_json_content():
    file = open(VOICE_GAME_FILE, "r")
    json_object = json.load(file)
    file.close()
    return json_object
