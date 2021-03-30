from enum import Enum, auto
from telegram import Update, ChatAction
from telegram.ext import CallbackContext
import yfinance as yf
import mplfinance as mpf

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors, send_action


class UserTimeInput(Enum):
    NOW = auto()
    DAY = auto()
    WEEK = auto()
    MONTH = auto()
    QUARTER = auto()
    YEAR = auto()


@register_module()
class FinanceBot(AbstractModule):
    @register_command(command="stonks",
                      short_desc="Sends a chart of a specified finance 📈",
                      long_desc=f"This command sends a candle-chart of a specified finance "
                                f"symbol in a given time period.\n"
                                f"Following time period specifications are supported: \n"
                                f"_{', '.join(list(UserTimeInput.__members__))}_",
                      usage=["/stonks BTC-EUR", "/stonks AAPL month", "/stonks DOGE-USD year"])
    @log_errors()
    @send_action(action=ChatAction.UPLOAD_PHOTO)
    def send_stock_command(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/stonks", update)
        if not query:
            update.message.reply_text("parameter angeben bitte...")
            return

        parts = query.split(" ")
        stock_name = parts[0]
        if len(parts) > 1:
            user_time_input = parts[1].upper()
        else:
            user_time_input = UserTimeInput.WEEK.name

        _send_stock(stock_name, user_time_input, update, context)


def _send_stock(stock_name: str, user_time_input_str: str, update, context):
    # volume = true
    ticker = yf.Ticker(stock_name)
    data_fetch_functions = {
        UserTimeInput.NOW: lambda: ticker.history(period="90m", interval="2m"),
        UserTimeInput.DAY: lambda: ticker.history(period="1d", interval="15m"),
        UserTimeInput.WEEK: lambda: ticker.history(period="1wk", interval="90m"),
        UserTimeInput.MONTH: lambda: ticker.history(period="1mo", interval="1d"),
        UserTimeInput.QUARTER: lambda: ticker.history(period="3mo", interval="1d"),
        UserTimeInput.YEAR: lambda: ticker.history(period="1y", interval="1d"),
    }
    user_time_input_str = user_time_input_str.upper()
    members = UserTimeInput.__members__
    if user_time_input_str in members:
        user_time_input = members[user_time_input_str]
        df = data_fetch_functions[user_time_input]()
        if df.shape[0] == 0:
            # No data found for specified stock or time
            update.message.reply_text(f"Hmm, na.. {stock_name} kenn i leider ned.")
        else:
            image_path = "./images/finance.png"
            mpf.plot(df,
                     type="candle", style="yahoo",
                     title=f"{stock_name} {user_time_input.name}",
                     savefig=image_path)
            context.bot.send_photo(chat_id=update.message.chat_id, photo=open(image_path, "rb"))
    else:
        # Wrong time specification
        update.message.reply_text("Sorry, aber des Zeitintervall sogt ma goa nix.\nZur Not hätt i a /help Kommando.")
