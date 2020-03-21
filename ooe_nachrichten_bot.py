import requests
from xml.dom import minidom


def get_newest_news(bot, update):
    query = get_command_parameter("/news", update)
    if query is None or query.isdigit():
        r = requests.get("https://www.nachrichten.at/storage/rss/rss/nachrichten.xml")
        parsed = minidom.parseString(r.text)
        try:
            text = ""
            if query is not None:
                if int(query) > 4:
                    query = 4
                for i in range(int(query)):
                    newest = parsed.getElementsByTagName("item")[i]
                    title = newest.getElementsByTagName("title")[0].firstChild.data
                    link = newest.getElementsByTagName("link")[0].firstChild.data
                    descr = newest.getElementsByTagName("description")[0].firstChild.data
                    text += title + "\n" + link + "\n" + descr + "\n \n \n"
            else:
                newest = parsed.getElementsByTagName("item")[0]
                title = newest.getElementsByTagName("title")[0].firstChild.data
                link = newest.getElementsByTagName("link")[0].firstChild.data
                descr = newest.getElementsByTagName("description")[0].firstChild.data
                text += title + "\n" + link + "\n" + descr + "\n"

            chat_id = update.message.chat_id
            bot.send_message(chat_id=chat_id, text=text)
        except:
            update.message.reply_text("Leider nix gfunden ☹️")
    else:
        update.message.reply_text("Du musst a Zahl eingeben du Floschn!️")


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command + " "):
        return text[len(command) + 1:]
    if text.startswith(command + b + " "):
        return text[len(command + b) + 1:]
