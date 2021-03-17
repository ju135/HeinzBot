import random

import praw
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultArticle, \
    InputTextMessageContent, InlineQueryResultVideo
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.api_key_reader import read_key
from utils.decorators import register_module, register_command, register_incline_cap, log_errors

CLIENT_ID = read_key("reddit-client-id")
CLIENT_SECRET = read_key("reddit-client-secret")
INLINE_QUERY_CACHE_TIME = 0


@register_module()
class RedditBot(AbstractModule):
    @register_command(command="reddit",
                      short_desc="Searches Reddit submissions. 😎",
                      long_desc="Sends an image or video from one of the top 30 hot [Reddit](https://reddit.com/)"
                                " submissions related to a given subreddit. The index is chosen randomly or can "
                                "be specified (starting at 0 for the hottest submission).",
                      usage=["/reddit $subreddit", "/reddit $subreddit $index", "/reddit memes", "/reddit memes 4"])
    @log_errors()
    def send_subreddit_submission(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        query = self.get_command_parameter("/reddit", update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return
        (subredditpath, index) = _get_subreddit_and_index(query)
        submission = _get_submission_for_subreddit_name(subredditpath, 30, index)
        if submission is None:
            update.message.reply_text("Sorry, nix gfunden.😢")
        else:
            if submission.is_video:
                print(submission.media['reddit_video']['fallback_url'])
                link = self.downsize_dash_link(submission.media['reddit_video']['fallback_url'], maximum_size=360)
                self.send_and_save_video(update=update, context=context,
                                         vide_url=link,
                                         command="/reddit",
                                         caption=submission.title)

            elif _get_external_video_link(submission) is not None:
                link = _get_external_video_link(submission)
                self.send_and_save_video(update=update, context=context,
                                         vide_url=self.downsize_dash_link(link, maximum_size=360),
                                         command="/reddit",
                                         caption=submission.title)
            else:
                self.send_and_save_picture(update=update, context=context,
                                           image_url=submission.url,
                                           command="/reddit",
                                           caption=submission.title)

    @register_command(command="funny",
                      short_desc="Sends a funny Reddit submission. 👌",
                      long_desc="Searches the [r/funny](https://www.reddit.com/r/funny/) "
                                "subreddit for submissions and returns a "
                                "random image/video submission of the top 25 hot posts.", usage=["/funny"])
    def send_funny_submission(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        submission = _get_submission_for_subreddit_name("funny", 25, None)
        if submission is None:
            update.message.reply_text("Sorry, nix gfunden.😢")
        else:
            if submission.is_video:
                link = self.downsize_dash_link(submission.media['reddit_video']['fallback_url'], maximum_size=360)
                self.send_and_save_video(update=update, context=context,
                                         vide_url=link,
                                         command="reddit",
                                         caption=submission.title)
            else:
                self.send_and_save_picture(update=update, context=context,
                                           image_url=submission.url,
                                           command="/reddit",
                                           caption=submission.title)
            # bot.send_photo(chat_id=chat_id, photo=url, caption=title)

    @register_incline_cap()
    def inline_caps(self, update: Update, context: CallbackContext):
        query, offset = _read_input_and_offset(update.inline_query.query)
        results = list()
        if query == "":
            return
        subreddit, search_results = _get_matching_subreddit_and_search_results(query)
        # No subreddit existing for query
        if subreddit is None:
            message = f"No subreddit for \"{query}\"."
            if len(search_results) > 0:
                message += f"Possible alternatives:\n" \
                           f"{', '.join(map(lambda x: str(x), search_results))}"
            results.append(
                InlineQueryResultArticle(
                    id="0",
                    title='Reddit Search',
                    input_message_content=InputTextMessageContent(query),
                    description=message
                    # "Schreib irgendan spöttischen Text.\nA bissal spotten hot no kan gschodt."
                )
            )
            context.bot.answer_inline_query(update.inline_query.id, results)
            return

        fetch_amount = 20
        submissions = _get_submissions_for_subreddit(subreddit, fetch_amount, offset)

        if len(submissions) < 1:
            results.append(
                InlineQueryResultArticle(
                    id="0",
                    title='Reddit Search',
                    input_message_content=InputTextMessageContent(query),
                    description="No img/video submissions found for \"" + query + "\"."
                    # "Schreib irgendan spöttischen Text.\nA bissal spotten hot no kan gschodt."
                )
            )
            context.bot.answer_inline_query(update.inline_query.id, results, cache_time=INLINE_QUERY_CACHE_TIME)
            return

        current_id = 0
        for submission in submissions:
            results.append(_create_inline_result(submission, str(current_id)))
            current_id = current_id + 1

        context.bot.answer_inline_query(update.inline_query.id, results, cache_time=INLINE_QUERY_CACHE_TIME)


def _read_input_and_offset(query: str) -> (str, int):
    parts = query.split(" ")
    if len(parts) > 1:
        inp = parts[0]
        if parts[1].isdigit():
            offset = int(parts[1])
        else:
            offset = 0
        return inp, offset
    return query, 0


def _create_inline_result(submission, identifier: str):
    video_preview = _get_video_preview(submission)
    caption = f"{submission.subreddit_name_prefixed}: {submission.title}"
    mod = AbstractModule()
    if video_preview is not None:
        return InlineQueryResultVideo(
            id=identifier,
            video_url=mod.downsize_dash_link(video_preview["fallback_url"], 720),
            video_duration=video_preview["duration"],
            thumb_url=_get_thumbnail(submission),
            mime_type="video/mp4",
            title=submission.title,
            caption=caption
        )
    elif _is_gif_submission(submission):
        return InlineQueryResultVideo(
            id=identifier,
            video_url=submission.url,
            thumb_url=_get_thumbnail(submission),
            mime_type="video/mp4",
            title=submission.title,
            caption=caption
        )
    else:
        return InlineQueryResultPhoto(
            id=identifier,
            photo_url=submission.url,
            thumb_url=_get_thumbnail(submission),
            title=submission.title,
            description=submission.subreddit.display_name,
            caption=caption
        )


def _is_gif_submission(submission) -> bool:
    parts = submission.url.split(".")
    if len(parts) > 0 and "gif" in parts[-1]:
        return True
    return False


def _get_thumbnail(submission):
    if submission.thumbnail is not None and submission.thumbnail != "nsfw":
        return submission.thumbnail
    if hasattr(submission, "preview") and "images" in submission.preview:
        images = submission.preview["images"]
        if len(images) > 0:
            if "url" in images[0]:
                return images[0]["url"]
    print("no thumbnail")
    return "empy"


def _get_video_preview(submission):
    if hasattr(submission, "preview") and submission.preview is not None \
            and "reddit_video_preview" in submission.preview:
        return submission.preview["reddit_video_preview"]
    if hasattr(submission, "secure_media") and submission.secure_media is not None \
            and "reddit_video" in submission.secure_media:
        return submission.secure_media["reddit_video"]
    return None


def _get_matching_subreddit_and_search_results(subreddit_name):
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         user_agent='linux:at.heinzbot.janisch:v1.0.0 (by /u/so-oag)')
    search_results = reddit.subreddits.search_by_name(subreddit_name)
    matching_subreddits = list(filter(lambda x: str(x).lower() == subreddit_name.lower(), search_results))
    if len(matching_subreddits) < 1:
        return None, search_results
    return matching_subreddits[0], search_results


def _get_submissions_for_subreddit(subreddit, limit, offset=0):
    if offset > 50:
        offset = 50
    hot_submissions = subreddit.hot(limit=limit + offset)
    submissionlist = list()
    current = 0
    for submission in hot_submissions:
        if current < offset:
            current = current + 1
            continue
        if hasattr(submission, "post_hint") and submission.post_hint == "image":
            submissionlist.append(submission)
        if hasattr(submission, "is_video") and submission.is_video:
            submissionlist.append(submission)
        if _get_external_video_link(submission) is not None:
            submissionlist.append(submission)
    return submissionlist


def _get_submission_for_subreddit_name(subreddit_name, limit, index):
    subreddit, search_results = _get_matching_subreddit_and_search_results(subreddit_name)
    if subreddit is None:
        return None
    submission_list = _get_submissions_for_subreddit(subreddit, limit)

    if len(submission_list) == 0:
        return None

    if index is None or index < 0 or index > len(submission_list) - 1:
        index = random.randint(0, len(submission_list) - 1)
    return submission_list[index]


def _get_external_video_link(submission):
    if hasattr(submission, "post_hint") and hasattr(submission, "preview") \
            and "reddit_video_preview" in submission.preview and \
            "fallback_url" in submission.preview["reddit_video_preview"]:
        return submission.preview["reddit_video_preview"]["fallback_url"]
    return None


def _get_subreddit_and_index(query) -> (str, int):
    query_parts = query.split()
    subreddit = query_parts[0]
    if len(query_parts) > 1:
        if query_parts[1].isdigit():
            index = int(query_parts[1])
            return subreddit, index
    return subreddit, None
