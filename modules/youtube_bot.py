from telegram import Update
from telegram.ext import CallbackContext
from utils.api_key_reader import read_key
from googleapiclient.discovery import build
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command

DEVELOPER_KEY = read_key("youtube")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


@register_module()
class YoutubeBot(AbstractModule):
    @register_command(command="yt", short_desc="I schick da as erste youtube video wos i findt.",
                      long_desc="", usage=[""])
    def get_youtube(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter('/yt', update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return

        url = _youtube_search(query)
        if url != "":
            context.bot.send_message(chat_id=update.message.chat_id, text=url)
        else:
            update.message.reply_text("Sorry, nix gfunden.😢")


def _youtube_search(q, max_results=1, order="relevance", token=None, location=None, location_radius=None):
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
