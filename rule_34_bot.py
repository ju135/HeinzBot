import requests
from xml.dom import minidom


def fetch_porn(bot, update):
    query = query = '&'.join(get_command_parameter("/rule34", update).split())
    r = requests.get("https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags=" + query)
    parsed = minidom.parseString(r.text)
    try:
        img = parsed.childNodes[0].childNodes[0].attributes["file_url"].value
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=img)
    except:
        update.message.reply_text("Leider nix gfunden ☹️")


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command + " "):
        return text[len(command) + 1:]
    if text.startswith(command + b + " "):
        return text[len(command + b) + 1:]
