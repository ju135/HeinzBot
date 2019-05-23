import random

import praw
from APIKeyReader import read_key
import telegram
import logging

CLIENT_ID = read_key("reddit-client-id")
CLIENT_SECRET = read_key("reddit-client-secret")


def send_funny_submission(bot, update):
    chat_id = update.message.chat_id
    submission = get_funny_submission()
    if submission is None:
        update.message.reply_text("Sorry, nix gfunden.😢")
    else:
        if submission.is_video:
            send_video(bot, chat_id, submission.media['reddit_video']['fallback_url'], submission.title)
        else:
            send_photo(bot, chat_id, submission.url, submission.title)
        # bot.send_photo(chat_id=chat_id, photo=url, caption=title)


def get_funny_submission():
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         user_agent='linux:at.heinzbot.janisch:v1.0.0 (by /u/so-oag)')
    subreddit = reddit.subreddit("funny")
    # subreddit = reddit.subreddit("MyPeopleNeedMe")
    hot_submissions = subreddit.hot(limit=25)
    submissionlist = list()
    for submission in hot_submissions:
        if submission.post_hint == "image" or submission.is_video:
            submissionlist.append(submission)
        else:
            print(submission.post_hint)
    if len(submissionlist) == 0:
        return None
    # subimglist = list(filter(lambda x: x.post_hint == "image", submissionlist))
    index = random.randint(0, len(submissionlist) - 1)
    return submissionlist[index]


def send_video(bot, chat_id, url, caption):
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_VIDEO)
    bot.send_video(chat_id=chat_id, video=url,
                   caption=caption, supports_streaming=True)


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
