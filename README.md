# HeinzBot

An implementation of a Telegram Bot with the following capabilities:

* Sends gifs/images through a google search. 
* Sends random Reddit submissions from provided subreddits.
* University
  * Sends the location of a course before it starts.
* Is capable of sending austrian news.
* Performs youtube searches and sends a link to the best match.
* Contains various yes/no answers to help decision making.
* Sends various quote images.
* Sends austrian traffic information.
* Sends various comics.
* Checks daily for new XKCD comics and sends them if there are some. 
* Sends the daily menue of good restaurants in Hagenberg.
* Can invite colleagues for coffee at multiple locations.
* Can show a a variety of weather information for the selected region:
  * Rain radar
  * Storm tracking
  * Wind gusts and average
  * forecasts for a specific location
* Can translate a given sentence into various languages.
* Offers a voice game functionality where quotes with bad pronunciation have to be guessed.
* Sends urban dictionary entries


## Possible Extensions

* Join invite for coffee
* NLG conversation with bot
* forecast selectable model

## Contribution Guide
New functionality is added inside the [modules](modules)-folder. 
Each class has to inherit the abstract [Base-Module](modules/abstract_module.py) and has to be registered with the `@register_module()` decorator.
<br>
Inside a registered class, the following bot-functionality may be added:
* [General Command](#implement-a-general-command) - Triggered when the command is sent inside the chat.
* [Daily Command](#implement-a-daily-job) - Runs daily as a job at a specific time.
* Callback-Query-Handler - To interact with dynamic user inputs.

The functions built up on the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) API wrapper.
Refer to their [documentation](https://python-telegram-bot.readthedocs.io/en/stable/) for further implementation details on how 
to interact with the bot.
### Local Setup

To run/test functionality on your local machine, you need to [create
an own telegram bot](https://core.telegram.org/bots#6-botfather). Afterwards the api-keys have to be added
into a `api-keys.json` file, which must be created at the project root.<br>
The following structure is necessary to get modules with api-key-need to run:


```json
{
  "telegram": "your_telegram_bot_token",
  "youtube": "your_api_key",
  "ics-file-link": "calendar_ics_file",
  "reddit-client-id": "xxxx",
  "reddit-client-secret": "xxxx",
  "mittag_client_id": "xxxx",
  "mittag_client_secret": "xxxx",
  "spoon": "spoonacular_key",
  "rapid_urban_dict_secret": "rapid_urban_dict_api_key",
  "google_key": "xxxx",
  "google_cx": "xxxx"
}
``` 


### Implement a general Command
A general command is implemented inside a module by decorating it with `@register_command`. Usages and short/long
descriptions have to be specified - they will show up when calling
the bot's `/help` command. The `@send_action`decorater defines 
the action, that is displayed in telegram, while the command is executed.
<br>
The following code snippet shows the registration implementation of 
a command that sends a cat gif and will be callable by using the `/cat` command:

```python
from modules.abstract_module import AbstractModule
from utils.decorators import register_command, register_module, send_action
from telegram import Update, ChatAction
from telegram.ext import CallbackContext

# register the class as module
@register_module()
class CatBot(AbstractModule):
    @register_command(command="cat", short_desc="Sends a cat gif. 😺",
                      long_desc="A cat-gif from [Cat as a service](https://cataas.com) is sent.",
                      usage=["/cat"])
    @send_action(action=ChatAction.UPLOAD_VIDEO)
    def cat_command(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        # send the reply
        context.bot.send_animation(chat_id=chat_id, animation="https://cataas.com/c/gif")
```

### Implement a Daily Job
To implement a daily job, the `@run_daily` decorator can be used.
The decorated function will be called every day on the specified time. 
Keep in mind: the used **time-zone is UTC**. <br>
By using the `/start` or `/stop` command, chats may subscribe/unsubscribe
to this specified job. Job identification is based on the specified "name"-paramter.


The following code-snipped sends a comic every day into subscribed chats:
```python
import datetime
from modules.abstract_module import AbstractModule
from utils.decorators import run_daily, register_module
from telegram.ext import CallbackContext

# register the class as module
@register_module()
class ComicBot(AbstractModule):
    @run_daily(name="daily_comic", time=datetime.time(hour=14 - 1, minute=29, second=10))
    def send_new_comic(self, context: CallbackContext, chat_id: str):
        comic_url = get_new_comic_url()
        context.bot.send_photo(chat_id=chat_id, photo=comic_url,
                                   caption="New Comic")
```

## Used APIs

* Youtube API 
* Reddit API
* Inspirobot API
* cataas - Cat as a Service
* RSS Service from Nachrichten.at
* RSS Service from ÖAMTC
* xkcd.com
* Mittag.at API
* Urban Dictionary API
* Kachelmann-Wetter Storm/Rain/Wind - Tracking
* Google translate API
* Google Custom Search API

## Dependencies (see requirements.txt)

* python-telegram-bot
* requests
* beautifulsoup4
* google-api-python-client
* ics
* PRAW
* schedule
* Selenium
* googletrans
* feedparser
* gTTS
* lxml
