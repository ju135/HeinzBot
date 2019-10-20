from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from constants.members import getName, getTOP
from RandomText import get_random_coffee_starter, get_random_coffee_end


def sendCoffeeInvitation(bot, update):
    userid = update.message.from_user.id
    name = getName(userid)
    top = getTOP(userid)

    keyboard = [
        [InlineKeyboardButton("TOP {}".format(top), callback_data=str("host")),
        InlineKeyboardButton("wo anders", callback_data=str("other")),
        InlineKeyboardButton("FH", callback_data=str("FH"))]
    ]
    replyMarkup = InlineKeyboardMarkup(keyboard)

    firstText = get_random_coffee_starter().replace("$", name)
    update.message.reply_text(firstText, reply_markup=replyMarkup)


def sendCoffeeSticker(bot, update):
    #chatid = update.message.chat.id
    pass


def sendCoffeeLocation(bot, update):
    query = update.callback_query
    userid = query.from_user.id
    text = query.message.text
    text += "\n\n"

    end = get_random_coffee_end(query.data)
    if query.data == "host":
        end = end.replace("$", str(getTOP(userid)))
    text += end

    query.edit_message_text(text=text)