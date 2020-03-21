from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from Constants.members import getName, getTOP
from Utils.RandomText import get_random_string_of_messages_file

currentUpdate = None # the current invitation we are editing
coffee_message_constants_file = "Constants/Messages/coffee_messages.json"

# sends a coffee invitation with inline keyboard
def sendCoffeeInvitation(bot, update):
    userid = update.message.from_user.id
    name = getName(userid)
    top = getTOP(userid)

    keyboard = [
        [InlineKeyboardButton("TOP {}".format(top), callback_data=str("host")),
        InlineKeyboardButton("wo anders", callback_data=str("other")),
        InlineKeyboardButton("FH", callback_data=str("FH"))]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    firstText = get_random_string_of_messages_file(coffee_message_constants_file, ["starter"]).replace("$", name)
    update.message.reply_text(firstText, reply_markup=markup)
    global currentUpdate # set the current update users will reply to
    currentUpdate = update


# will send a variety of coffee stickers
def sendCoffeeSticker(bot, update):
    #chatid = update.message.chat.id
    pass


"""called when a location button in the inline keyboard was clicked,
will update the message with the location"""
def sendCoffeeLocation(bot, update):
    query = update.callback_query
    clickingUserID = query.from_user.id

    if currentUpdate == None or clickingUserID == currentUpdate.message.from_user.id:
        text = query.message.text   
        text += "\n\n"

        end = get_random_string_of_messages_file(coffee_message_constants_file, ["end", query.data])
        if query.data == "host": # if hosting, fill in the name, too.
            end = end.replace("$", str(getTOP(clickingUserID)))
        text += end

        query.edit_message_text(text=text)
    else:
        bot.send_message(chat_id=currentUpdate.message.chat.id,
                         text="Herst {}, hab i mid dia gredt?".format(getName(clickingUserID)))
