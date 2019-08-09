from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.request import urlopen
from googleapiclient.discovery import build
from APIKeyReader import read_key
import logging
import json

DEVELOPER_KEY = read_key("youtube")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)


def get_image(bot, update):
    query = get_command_parameter("/image", update)
    if not query:
        update.message.reply_text("parameter angeben bitte...")
        return
    query = percent_encoding(query).split()
    query = '+'.join(query)
    url = "https://www.google.co.in/search?q=" + query + "&tbm=isch"
    print(url)
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/43.0.2357.134 Safari/537.36 "
    }
    soup = get_soup(url, header)

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
        bot.send_photo(chat_id=chat_id, photo=img)


def get_gif(bot, update):
    query = get_command_parameter('/gif', update)
    if not query:
        update.message.reply_text("parameter angeben bitte...")
        return
    query = percent_encoding(query).split()
    query = '+'.join(query)
    url = "https://www.google.co.in/search?q=" + query + "&tbm=isch&tbs=itp:animated"
    print(url)
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/43.0.2357.134 Safari/537.36 "
    }
    soup = get_soup(url, header)

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
        bot.send_animation(chat_id=chat_id, animation=img)


def get_command_parameter(command: str, update) -> str:
    text = update.message.text
    b = update.message.bot.name
    if text.startswith(command+" "):
        return text[len(command)+1:]
    if text.startswith(command + b + " "):
        return text[len(command+b) + 1:]


def get_youtube(bot, update):
    query = get_command_parameter('/yt', update)
    if not query:
        update.message.reply_text("parameter angeben bitte...")
        return

    url = youtube_search(query)
    if url != "":
        bot.send_message(chat_id=update.message.chat_id, text=url)
    else:
        update.message.reply_text("Sorry, nix gfunden.😢")


def percent_encoding(string):
    result = ''
    accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
    for char in string.encode('utf-8'):
        result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
    return result


def get_soup(url, header):
    req = urllib.request.Request(url, headers=header)
    openurl = urlopen(req)
    soup = BeautifulSoup(openurl, "html.parser")
    return soup


def youtube_search(q, max_results=1, order="relevance", token=None, location=None, location_radius=None):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)

    # source: https://medium.com/greyatom/youtube-data-in-python-6147160c5833
    search_response = youtube.search().list(
        q=q,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",  # Part signifies the different types of data you want
        maxResults=max_results,
        location=location,
        locationRadius=location_radius).execute()

    url = ""
    if len(search_response.get("items", [])) > 0:
        video_id = search_response.get("items", [])[0]["id"]["videoId"]
        url = "https://www.youtube.com/watch?v=" + video_id

    return url
