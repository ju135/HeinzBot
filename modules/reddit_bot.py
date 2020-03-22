import random
import praw
from telegram import Update
from telegram.ext import CallbackContext
from utils.api_key_reader import read_key
import telegram
from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command

CLIENT_ID = read_key("reddit-client-id")
CLIENT_SECRET = read_key("reddit-client-secret")


@register_module()
class RedditBot(AbstractModule):
    @register_command(command="reddit",
                      text="Wennsd an subreddit angibst schick i da ans vo die top 30 hot bilder oder videos. 😎")
    def send_subreddit_submission(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        query = self.get_command_parameter("/reddit", update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return
        (subredditpath, index) = _get_subreddit_and_index(query)
        submission = _get_submission_for_subreddit(subredditpath, 30, index)
        if submission is None:
            update.message.reply_text("Sorry, nix gfunden.😢")
        else:
            if submission.is_video:
                print(submission.media['reddit_video']['fallback_url'])
                _send_video(context.bot, update, submission.media['reddit_video']['fallback_url'], submission.title)
            elif _get_external_video_link(submission) is not None:
                link = _get_external_video_link(submission)
                _send_video(context.bot, update, link, submission.title)
            else:
                _send_photo(context.bot, chat_id, submission.url, submission.title)

    @register_command(command="funny",
                      text="i schick da funny reddit submissions. 👌")
    def send_funny_submission(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        submission = _get_submission_for_subreddit("funny", 25, None)
        if submission is None:
            update.message.reply_text("Sorry, nix gfunden.😢")
        else:
            if submission.is_video:
                _send_video(context.bot, update, submission.media['reddit_video']['fallback_url'], submission.title)
            else:
                _send_photo(context.bot, chat_id, submission.url, submission.title)
            # bot.send_photo(chat_id=chat_id, photo=url, caption=title)


def _get_submission_for_subreddit(subreddit_name, limit, index):
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         user_agent='linux:at.heinzbot.janisch:v1.0.0 (by /u/so-oag)')
    subreddit = reddit.subreddit(subreddit_name)
    hot_submissions = subreddit.hot(limit=limit)
    submissionlist = list()
    try:
        for submission in hot_submissions:
            if hasattr(submission, "post_hint") and submission.post_hint == "image":
                submissionlist.append(submission)
            if hasattr(submission, "is_video") and submission.is_video:
                submissionlist.append(submission)
            if _get_external_video_link(submission) is not None:
                submissionlist.append(submission)
    except:
        return None

    if len(submissionlist) == 0:
        return None

    if index is None or index < 0 or index > len(submissionlist)-1:
        index = random.randint(0, len(submissionlist) - 1)
    return submissionlist[index]


def _get_external_video_link(submission):
    if hasattr(submission, "post_hint") and hasattr(submission, "preview") \
            and "reddit_video_preview" in submission.preview and "fallback_url" in submission.preview["reddit_video_preview"]:
        return submission.preview["reddit_video_preview"]["fallback_url"]
    return None


def _send_video(bot, update, url, caption):
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_VIDEO)
    resolution = int(url[url.rindex('DASH_')+5:].split('?')[0])
    new_url = url
    if resolution > 360:
        new_url = url[:url.rindex('/')+1] + "DASH_360"
    try:
        bot.send_video(chat_id=chat_id, video=new_url,
                        caption=caption, supports_streaming=True)
    except:
        update.message.reply_text("Irgendwos hot do ned highaut ☹️")


def _send_photo(bot, chat_id, url, caption):
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.send_photo(chat_id=chat_id, photo=url, caption=caption)


def _get_subreddit_and_index(query) -> (str, int):
    query_parts = query.split()
    subreddit = query_parts[0]
    if len(query_parts) > 1:
        if query_parts[1].isdigit():
            index = int(query_parts[1])
            return subreddit, index
    return subreddit, None

