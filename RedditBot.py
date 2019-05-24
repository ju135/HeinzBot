import random

import praw
from APIKeyReader import read_key
from GoogleSearch import get_command_parameter
import telegram
import logging

CLIENT_ID = read_key("reddit-client-id")
CLIENT_SECRET = read_key("reddit-client-secret")


def send_subreddit_submission(bot, update):
    chat_id = update.message.chat_id
    query = get_command_parameter("/reddit", update)
    if not query:
        update.message.reply_text("parameter angeben bitte...")
        return
    submission = get_submission_for_subreddit(query, 30)
    if submission is None:
        update.message.reply_text("Sorry, nix gfunden.😢")
    else:
        if submission.is_video:
            print(submission.media['reddit_video']['fallback_url'])
            send_video(bot, update, submission.media['reddit_video']['fallback_url'], submission.title)
        else:
            send_photo(bot, chat_id, submission.url, submission.title)


def send_funny_submission(bot, update):
    chat_id = update.message.chat_id
    submission = get_submission_for_subreddit("funny", 25)
    if submission is None:
        update.message.reply_text("Sorry, nix gfunden.😢")
    else:
        if submission.is_video:
            send_video(bot, update, submission.media['reddit_video']['fallback_url'], submission.title)
        else:
            send_photo(bot, chat_id, submission.url, submission.title)
        # bot.send_photo(chat_id=chat_id, photo=url, caption=title)


def get_submission_for_subreddit(subreddit_name, limit):
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
    except:
        return None

    if len(submissionlist) == 0:
        return None
    index = random.randint(0, len(submissionlist) - 1)
    return submissionlist[index]


def send_video(bot, update, url, caption):
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


def send_photo(bot, chat_id, url, caption):
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.send_photo(chat_id=chat_id, photo=url, caption=caption)


def main():
    (url, title) = get_funny_image()
    print(url)
    print(title)


def start_logger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger('prawcore')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


if __name__ == '__main__':
    main()
